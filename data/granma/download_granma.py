import httpx
import datetime
import os
import re


start = datetime.datetime(2014, 1, 1)
end = datetime.datetime(2025, 4, 30)

date = start

while date <= end:
    try:
        print(date.strftime("%Y-%m-%d"))

        filename = date.strftime("%Y/%m/Gramna-%Y-%m-%d.pdf")

        if os.path.exists(filename):
            date += datetime.timedelta(days=1)
            continue

        url = f"https://www.granma.cu/impreso/{date.strftime('%Y-%m-%d')}"

        response = httpx.get(url)

        if response.status_code != 200:
            date += datetime.timedelta(days=1)
            continue

        # extract hrefs from the response
        hrefs = re.findall(r'href=[\'"]?([^\'" >]+)', response.text)

        # filter hrefs that contain "G_2023101001.pdf"

        hrefs = [href for href in hrefs if "G_" in href and ".pdf" in href]

        if len(hrefs) == 0:
            date += datetime.timedelta(days=1)
            continue

        print(hrefs[0])

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        response = httpx.get("https://www.granma.cu" + hrefs[0])

        if response.status_code != 200:
            continue

        with open(filename, "wb") as f:
            f.write(response.content)

    except httpx.TimeoutException:
        pass

    date += datetime.timedelta(days=1)
