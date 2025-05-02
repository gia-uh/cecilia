import httpx
import datetime
import os
import re


start = datetime.datetime(2014, 1, 1)
end = datetime.datetime(2025,4,30)

date = start

while date <= end:
    try:
        print(date.strftime("%Y-%m-%d"))

        filename = date.strftime("%Y/%m/JR-%Y-%m-%d.pdf")

        if os.path.exists(filename):
            date += datetime.timedelta(days=1)
            continue

        url = f"https://www.juventudrebelde.cu/printed/{date.strftime('%Y/%m/%d')}/icompleta.pdf"
        response = httpx.get(url)

        if response.status_code != 200:
            date += datetime.timedelta(days=1)
            continue

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "wb") as f:
            f.write(response.content)

    except httpx.TimeoutException:
        pass

    date += datetime.timedelta(days=1)
