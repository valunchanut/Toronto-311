import re
import io
import requests
import pandas as pd

BASE = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
PKG_ID = "311-service-requests-customer-initiated"

YEAR_RX = re.compile(r"(20\d{2})")

def discover_year_resources(want_years):
    """Return {year: resource_dict} for the package, filtered to want_years."""
    pkg = requests.get(f"{BASE}/api/3/action/package_show", params={"id": PKG_ID}).json()
    resources = pkg["result"]["resources"]
    year_map = {}
    for r in resources:
        name = f"{r.get('name','')} {r.get('description','')}"
        m = YEAR_RX.search(name)
        if m:
            y = int(m.group(1))
            if y in want_years:
                year_map[y] = r
    return dict(sorted(year_map.items()))

def ds_sql(sql: str) -> pd.DataFrame:
    res = requests.get(f"{BASE}/api/3/action/datastore_search_sql", params={"sql": sql}).json()
    if not res.get("success"):
        raise RuntimeError(res)
    return pd.DataFrame(res["result"]["records"])

def pull_year_counts(resource, exclude_canceled=True) -> pd.DataFrame:
    """Aggregate counts by year/type/division/ward for a resource, via SQL or CSV."""
    if resource.get("datastore_active"):
        where = "WHERE COALESCE(\"Service Request Status\",'') <> 'Canceled'" if exclude_canceled else ""
        sql = f"""        SELECT
          date_part('year', "Service Request Creation Date and Time")::int AS year,
          "Original Service Request Type" AS type,
          "Service Request Division" AS division,
          "Service Request Ward" AS ward,
          COUNT(*) AS n
        FROM "{resource['id']}"
        {where}
        GROUP BY 1,2,3,4
        """
        df = ds_sql(sql)
        return df.astype({"year": int, "n": int})
    else:
        raw = requests.get(resource["url"]).content
        df = pd.read_csv(io.BytesIO(raw))
        ren = {c: c.strip() for c in df.columns}
        df = df.rename(columns=ren)
        dt = pd.to_datetime(df["Service Request Creation Date and Time"], errors="coerce", utc=True)
        df = df.assign(dt=dt).dropna(subset=["dt", "Original Service Request Type"])
        if exclude_canceled:
            df = df[df["Service Request Status"].fillna("") != "Canceled"]
        g = (df.assign(year=df["dt"].dt.year)
                .groupby(["year","Original Service Request Type","Service Request Division","Service Request Ward"]).size()
                .reset_index(name="n"))
        g.columns = ["year","type","division","ward","n"]
        return g.astype({"year": int, "n": int})

def pull_daily(resource, exclude_canceled=True) -> pd.DataFrame:
    if resource.get("datastore_active"):
        where = "WHERE COALESCE(\"Service Request Status\",'') <> 'Canceled'" if exclude_canceled else ""
        sql = f"""        SELECT
          date_trunc('day', "Service Request Creation Date and Time")::date AS day,
          COUNT(*) AS n
        FROM "{resource['id']}"
        {where}
        GROUP BY 1
        ORDER BY 1
        """
        return ds_sql(sql)
    else:
        raw = requests.get(resource["url"]).content
        df = pd.read_csv(io.BytesIO(raw))
        dt = pd.to_datetime(df["Service Request Creation Date and Time"], errors="coerce", utc=True)
        df = df.assign(day=dt.dt.date)
        if exclude_canceled:
            df = df[df["Service Request Status"].fillna("") != "Canceled"]
        g = df.groupby("day").size().reset_index(name="n")
        return g
