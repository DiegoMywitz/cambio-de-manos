"""Ping periódico a la app pública para que Streamlit Cloud no la ponga a dormir
por inactividad. Se programa aparte (Task Scheduler de Windows), no corre solo.
"""

import sys

import requests

APP_URL = "https://cambiodemanos.streamlit.app/"


def main():
    try:
        r = requests.get(APP_URL, timeout=30)
        print(f"Ping a {APP_URL}: status {r.status_code}")
    except Exception as e:
        print(f"Ping a {APP_URL} falló: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
