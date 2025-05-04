import streamlit as st
import sqlite3
import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt

# Database and XML paths
db_path = "oxfordshire_data.db"
xml_path = "CouncilTaxData.xml"

# Helper functions
def run_query(query, params=()):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

st.title("Oxfordshire Data Explorer (Streamlit Version)")

# House Price Section
st.header("House Price Queries")
wards = pd.read_sql_query("SELECT DISTINCT ward_name FROM HousePrice", sqlite3.connect(db_path))['ward_name'].tolist()
selected_ward = st.selectbox("Select Ward", wards)
year1 = st.number_input("Year 1", min_value=1995, max_value=2025, value=2020)
year2 = st.number_input("Year 2", min_value=1995, max_value=2025, value=2023)

if st.button("Average Price"):
    result = run_query("SELECT AVG(price) FROM HousePrice WHERE ward_name = ? AND (year = ? OR year = ?)", (selected_ward, year1, year2))
    st.write(f"Average price: £{result[0][0]:.2f}")

if st.button("Price Change %"):
    price1 = run_query("SELECT AVG(price) FROM HousePrice WHERE ward_name = ? AND year = ?", (selected_ward, year1))[0][0]
    price2 = run_query("SELECT AVG(price) FROM HousePrice WHERE ward_name = ? AND year = ?", (selected_ward, year2))[0][0]
    change = ((price2 - price1) / price1) * 100
    st.write(f"Price Change: {change:.2f}%")

st.subheader("Lowest Price in District")
districts = pd.read_sql_query("SELECT DISTINCT local_auth_name FROM HousePrice", sqlite3.connect(db_path))['local_auth_name'].tolist()
district = st.selectbox("Select District", districts)
year = st.number_input("Year", min_value=1995, max_value=2025, value=2022, key='low_year')
quarter = st.selectbox("Quarter", ["Mar", "Jun", "Sep", "Dec"])

if st.button("Find Lowest Price"):
    result = run_query("SELECT ward_name, MIN(price) FROM HousePrice WHERE local_auth_name = ? AND year = ? AND quarter = ?", (district, year, quarter))
    st.write(f"Lowest price: {result[0][0]} - £{result[0][1]:.2f}")

# Broadband Section
st.header("Broadband Queries")
bb_areas = pd.read_sql_query("SELECT [Area name] FROM BroadBandData", sqlite3.connect(db_path))['Area name'].tolist()
bb_area = st.selectbox("Select Area", bb_areas)

if st.button("Show Broadband Info"):
    result = run_query("SELECT * FROM BroadBandData WHERE [Area name] = ?", (bb_area,))
    st.write(result)

if st.button("Areas with Low Gigabit Availability"):
    result = run_query("SELECT [Area name] FROM BroadBandData WHERE [Gigabit availability] < 0.5")
    st.write([r[0] for r in result])

# Council Tax Section
st.header("Council Tax SQL Queries")
towns = pd.read_sql_query("SELECT DISTINCT TownName FROM CouncilTax", sqlite3.connect(db_path))['TownName'].tolist()
town1 = st.selectbox("Town 1", towns)
town2 = st.selectbox("Town 2", towns)
band = st.selectbox("Band", ["A", "B", "C", "D", "E", "F", "G", "H"])

if st.button("Council Tax Difference"):
    charge1 = run_query("SELECT Charge FROM CouncilTax WHERE TownName = ? AND Band = ?", (town1, band))[0][0]
    charge2 = run_query("SELECT Charge FROM CouncilTax WHERE TownName = ? AND Band = ?", (town2, band))[0][0]
    st.write(f"Difference: £{abs(charge1 - charge2):.2f}")

if st.button("Lowest Band B Tax Town"):
    result = run_query("SELECT TownName, MIN(Charge) FROM CouncilTax WHERE Band = 'B'")
    st.write(f"Lowest Band B: {result[0][0]} - £{result[0][1]:.2f}")

# XML Tasks
st.header("Council Tax XML Queries")
band_xml = st.selectbox("Band for Average Tax", ["A", "B", "C"])

if st.button("Average Council Tax (XML)"):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    charges = [float(b.attrib['charge']) for t in root.findall("Town") for b in t.findall("Band") if b.attrib['name'] == band_xml]
    avg = sum(charges) / len(charges)
    st.write(f"Average Council Tax for Band {band_xml}: £{avg:.2f}")

if st.button("Highest Band C Tax (XML)"):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    highest = ("", 0)
    for town in root.findall("Town"):
        for band in town.findall("Band"):
            if band.attrib['name'] == "C" and float(band.attrib['charge']) > highest[1]:
                highest = (town.attrib['name'], float(band.attrib['charge']))
    st.write(f"Highest Band C: {highest[0]} - £{highest[1]:.2f}")

# Visualisation
st.header("Visualisation")

if st.button("Show Oxford Wards Graph"):
    conn = sqlite3.connect(db_path)
    wards = ["Summertown", "Barton", "Marston", "Osney, Jericho & Port Meadow", "Wolvercote & Cutteslowe"]
    plt.figure(figsize=(10,5))
    for ward in wards:
        df = pd.read_sql_query("SELECT year, quarter, price FROM HousePrice WHERE ward_name = ? AND year >= 2013", conn, params=(ward,))
        df['Quarter'] = df['year'].astype(str) + " " + df['quarter']
        plt.plot(df['Quarter'], df['price'], marker='o', label=ward)
    plt.xticks(rotation=90)
    plt.legend()
    plt.title("Oxford Wards House Prices")
    st.pyplot(plt)

if st.button("Show Cherwell Wards Graph"):
    wards = ["Banbury Grimsbury and Hightown", "Banbury Cross and Neithrop", "Bicester East", "Kidlington East", "Deddington"]
    data = pd.DataFrame()
    conn = sqlite3.connect(db_path)
    for ward in wards:
        df = pd.read_sql_query("SELECT price FROM HousePrice WHERE ward_name = ? AND year >= 2013", conn, params=(ward,))
        df['Ward'] = ward
        data = pd.concat([data, df])
    avg_prices = data.groupby("Ward")["price"].mean()
    avg_prices.plot(kind='bar', title="Cherwell Wards Avg House Prices")
    st.pyplot(plt)
