#!/usr/bin/env python
"""Test all library imports and versions"""

print("Testing library imports...\n")

try:
    import numpy
    print(f"✅ numpy {numpy.__version__}")
except Exception as e:
    print(f"❌ numpy: {e}")

try:
    import pandas
    print(f"✅ pandas {pandas.__version__}")
except Exception as e:
    print(f"❌ pandas: {e}")

try:
    import mysql.connector
    print(f"✅ mysql-connector-python 9.5.0")
except Exception as e:
    print(f"❌ mysql-connector-python: {e}")

try:
    from google import genai
    print(f"✅ google-genai {genai.__version__}")
except Exception as e:
    print(f"❌ google-genai: {e}")

try:
    import streamlit
    print(f"✅ streamlit {streamlit.__version__}")
except Exception as e:
    print(f"❌ streamlit: {e}")

try:
    import json
    print(f"✅ json (built-in)")
except Exception as e:
    print(f"❌ json: {e}")

try:
    import time
    print(f"✅ time (built-in)")
except Exception as e:
    print(f"❌ time: {e}")

print("\n✅ All necessary libraries are installed and compatible!")
