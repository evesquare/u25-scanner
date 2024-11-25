import json
import re
from datetime import datetime, timedelta
from pprint import pprint

import chompjs
import requests


def extract_availability_string(content):
    """
    Extract only the Aswbed.AvailabilityResultObj string from content

    Args:
        content (str): Input content containing the availability data

    Returns:
        str: Extracted Aswbed.AvailabilityResultObj string
    """
    start = "Aswbed.AvailabilityResultObj = "
    end = "</script>"

    # Find the start position
    start_pos = content.find(start)
    if start_pos == -1:
        raise ValueError("Could not find Aswbed.AvailabilityResultObj")

    # Find the end position from the start
    content_from_start = content[start_pos + len(start) :]
    end_pos = content_from_start.find(end)
    if end_pos == 0:  # -1 + 1 = 0
        raise ValueError("Could not find the end of object")

    # Extract the string
    result = content_from_start[:end_pos]
    return result


def request_ana():

    now = datetime.now()
    tomorrow = now + timedelta(days=1)

    now_timestamp = now.strftime("%Y%m%d%H%M%S")

    data = {
        "departureAirport": "HND",
        "arrivalAirport": "OKA",
        "roundFlag": "0",
        "outboundBoardingDate": now.strftime("%Y%m%d"),
        "inboundBoardingDate": tomorrow.strftime("%Y%m%d"),
        "adultCount": "1",
        "childCount": "0",
        "infantCount": "0",
        "compartmentClass": "Y",
        "searchMode": "0",
    }

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Host": "aswbe-d.ana.co.jp",
        "Origin": "https://www.ana.co.jp",
        "Referer": "https://www.ana.co.jp/",
    }

    session = requests.Session()

    post_url = f"https://aswbe-d.ana.co.jp/Axkow23/dms/redbe/dyc/be/pages/res/search/vacantEntranceDispatch.xhtml?rand={now_timestamp}&CONNECTION_KIND=JPN&LANG=ja"
    session.post(post_url, data=data, headers=headers)

    get_url = f"https://aswbe-d.ana.co.jp/9Eile48/dms/red21p/dyc/be/pages/res/search/vacantResult.xhtml?rand={now_timestamp}&aswdcid=1"
    get_response = session.get(get_url, headers=headers)

    # レスポンスのHTMLの中から必要な部分を取得
    result_object = extract_availability_string(get_response.text)

    session.close()

    return chompjs.parse_js_object(result_object)


def main():
    result = request_ana()
    for i in result:
        if result[i]["FareInfo"][0]["name"] != "スマートU25":
            continue
        select_segment_info = result[i]["SubmitInfo"]["SelectSegmentInfo"]

        if select_segment_info == []:
            continue

        print("====================================================")
        segment_info = result[i]["SubmitInfo"]["SelectSegmentInfo"][0]
        print(
            "搭乗日: "
            + segment_info["boardingYear"]
            + "年"
            + segment_info["boardingMonth"]
            + "月"
            + segment_info["boardingDay"]
            + "日"
            + segment_info["deptTime"][:2]
            + "時"
            + segment_info["deptTime"][2:]
            + "分"
        )
        print(
            "空路: "
            + segment_info["arvlAirportCode"]
            + " -> "
            + segment_info["deptAirportCode"]
        )
        print("金額: " + segment_info["price"])
        print("====================================================")


if __name__ == "__main__":
    main()
