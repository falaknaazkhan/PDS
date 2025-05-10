import streamlit as st
import sqlite3
import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt

# Database and XML paths
db_path = "final/final_oxfordshire.db"
xml_path = "CouncilTaxData.xml"

# Helper functions
def run_query(query, params=()):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

st.title("Oxfordshire Data Explorer")

# House Price Section
st.header("House Price Queries")
# Task 4: Average house price in 2 years
wards = pd.read_sql_query("SELECT DISTINCT ward_name FROM District", sqlite3.connect(db_path))['ward_name'].tolist()
selected_ward = st.selectbox("Select Ward", wards)
ward_id = run_query("SELECT DISTINCT ward_id FROM District WHERE ward_name = ?", (selected_ward,))[0][0]
year1 = st.number_input("Year 1", min_value=1995, max_value=2025, value=2020)
year2 = st.number_input("Year 2", min_value=1995, max_value=2025, value=2023)

if st.button("Average Price"):
    result = run_query("SELECT AVG(price) FROM HousePrice WHERE ward_id = ? AND year IN (?, ?)", (ward_id, year1, year2))
    st.write(f"Average price: £{result[0][0]:.2f}")

# Task 5: Price change %
if st.button("Price Change %"):
    price1 = run_query("SELECT AVG(price) FROM HousePrice WHERE ward_id = ? AND year = ? LIMIT 1", (ward_id, year1))[0][0]
    price2 = run_query("SELECT AVG(price) FROM HousePrice WHERE ward_id = ? AND year = ? LIMIT 1", (ward_id, year2))[0][0]
    change = ((price2 - price1) / price1) * 100
    st.write(f"Price Change: {change:.2f}%")

# Task 6: Lowest price in a district by quarter
st.subheader("Lowest Price in District")
districts = pd.read_sql_query("SELECT DISTINCT district_name FROM District", sqlite3.connect(db_path))['district_name'].tolist()
district = st.selectbox("Select District", districts)
district_id= run_query("SELECT district_id FROM District WHERE district_name = ? LIMIT 1", (district,))[0][0]
year = st.number_input("Year", min_value=1995, max_value=2025, value=2022, key='low_year')
quarter = st.selectbox("Quarter", ["Mar", "Jun", "Sep", "Dec"])

if st.button("Find Lowest Price"):
    # result = run_query("SELECT d.ward_name, MIN(hp.price) FROM HousePrice as hp, District as d WHERE hp.district_id = ? AND hp.year = ? AND hp.quarter = ?", (district_id ,year, quarter))
    result = run_query(""" SELECT d.ward_name, MIN(hp.price) FROM HousePrice hp JOIN District d ON hp.ward_id = d.ward_id WHERE hp.district_id = ? AND hp.year = ? AND hp.quarter = ? """, (district_id, year, quarter))
    if result and result[0][1] is not None:
        st.write(f"Lowest price: {result[0][0]} - £{result[0][1]:.2f}")
    else:
        st.warning(f"No price data found for {district}")

# Broadband Section
st.header("Broadband Queries")
# Task 7: Broadband info by area
bb_areas = pd.read_sql_query("SELECT [area_name] FROM Area", sqlite3.connect(db_path))['area_name'].tolist()
bb_area = st.selectbox("Select Area", bb_areas)
bb_area_id = run_query("SELECT area_id FROM Area WHERE [area_name] = ?", (bb_area,))[0][0]
if st.button("Show Broadband Info"):
    result = run_query("SELECT 'Average download speed', [avg_download_speed], 'Superfast availability', [superfast_availability], 'Gigabit availability', [gigabit_availability] FROM BroadBand WHERE [area_id] = ?", (bb_area_id,)) # trial code
    st.write(f"{result[0][0]}: {result[0][1]:.2f}  \n {result[0][2]}: {result[0][3]:.2f}  \n {result[0][4]}: {result[0][5]:.2f}")

# Task 7: Broadband by postcode
st.header("Broadband Info by Postcode")
postcode_input = st.text_input("Enter a postcode (e.g., OX3 0FG, ox4 1fy):").strip().upper()
if postcode_input:
    result = run_query("""
        SELECT 
            A.area_name,
            B.avg_download_speed,
            B.superfast_availability
        FROM PostCode P
        JOIN Area A ON P.area_id = A.area_id
        JOIN Broadband B ON A.area_id = B.area_id
        WHERE P.postcode = ?
    """, (postcode_input,))

    if result:
        st.write(f"Area: {result[0][0]}")
        st.write(f"Average Download Speed: {result[0][1]:.2f} Mbps")
        st.write(f"Superfast Broadband Availability: {result[0][2]:.2f}%")
    else:
        st.warning("No broadband data found for this postcode.")


# Task 8: Custom broadband query
if st.button("Areas with Low Gigabit Availability"):
    result = run_query("SELECT [area_id] FROM BroadBand WHERE [gigabit_availability] < 0.5")
    area_ids = [r[0] for r in result]
    placeholders = ','.join(['?'] * len(area_ids))  # Create ?,?,?... depending on number of items
    query = f"SELECT area_name FROM Area WHERE area_id IN ({placeholders})"
    result_name = run_query(query, area_ids)
    st.write("Areas with Low Gigabit Availability are:  \n" + "  \n ".join(r[0] for r in result_name))

# Council Tax Section
# Council Tax SQL Queries (Tasks 9–10)
st.header("Council Tax SQL Queries")
towns = pd.read_sql_query("SELECT DISTINCT town_name FROM CouncilTax", sqlite3.connect(db_path))['town_name'].tolist()
town1 = st.selectbox("Town 1", towns)
town2 = st.selectbox("Town 2", towns)
band = st.selectbox("Band", ["A", "B", "C", "D", "E", "F", "G", "H"])

if st.button("Council Tax Difference"):
    charge1 = run_query("SELECT charge FROM CouncilTax WHERE town_name = ? AND band = ?", (town1, band))[0][0]
    charge2 = run_query("SELECT charge FROM CouncilTax WHERE town_name = ? AND band = ?", (town2, band))[0][0]
    st.write(f"Difference: £{abs(charge1 - charge2):.2f}")

if st.button("Lowest Band B Tax Town"):
    result = run_query("SELECT town_name, MIN(charge) FROM CouncilTax WHERE band = 'B'")
    st.write(f"Lowest Band B: {result[0][0]} - £{result[0][1]:.2f}")

# XML Tasks
st.header("Council Tax XML Queries")
band_xml = st.selectbox("Band for Average Tax", ["A", "B", "C"])

if st.button("Average Council Tax (XML)"):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        charges = [float(b.attrib['charge']) for t in root.findall("Town") for b in t.findall("Band") if b.attrib['name'] == band_xml]
        avg = sum(charges) / len(charges)
        st.write(f"Average Council Tax for Band {band_xml}: £{avg:.2f}")
    except Exception as e:
        st.error(f"XML error: {e}")

if st.button("Highest Band C Tax (XML)"):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        highest = ("", 0)
        for town in root.findall("Town"):
            for band in town.findall("Band"):
                if band.attrib['name'] == "C" and float(band.attrib['charge']) > highest[1]:
                    highest = (town.attrib['name'], float(band.attrib['charge']))
        st.write(f"Highest Band C: {highest[0]} - £{highest[1]:.2f}")
    except Exception as e:
        st.error(f"XML error: {e}")

# Oxford Wards - Line Plot
st.header("Visualisation")
st.subheader("Oxford Wards - Line Plot Visualization")

# Connect and get ward names that have house price data from 2013 onward
conn = sqlite3.connect(db_path)
wards_with_data = pd.read_sql_query("""
    SELECT DISTINCT D.ward_name 
    FROM HousePrice HP
    JOIN District D ON HP.ward_id = D.ward_id
    WHERE HP.year >= 2013
    ORDER BY D.ward_name
""", conn)['ward_name'].tolist()

# Multi-select for user
selected_wards = st.multiselect("Select one or more wards to visualize:", wards_with_data)

# if st.button("Show House Price Trends") and selected_wards:
if st.button("Show House Price Trends"):
    if selected_wards:
        plt.figure(figsize=(12, 6))
        for ward in selected_wards:
            df = pd.read_sql_query("""
                SELECT HP.year, HP.quarter, HP.price 
                FROM HousePrice HP
                JOIN District D ON HP.ward_id = D.ward_id
                WHERE D.ward_name = ? AND HP.year >= 2013
                ORDER BY HP.year, 
                        CASE HP.quarter 
                            WHEN 'Mar' THEN 1 
                            WHEN 'Jun' THEN 2 
                            WHEN 'Sep' THEN 3 
                            WHEN 'Dec' THEN 4 
                        END
            """, conn, params=(ward,))
            if not df.empty:
                df['Quarter'] = df['year'].astype(str) + " " + df['quarter']
                plt.plot(df['Quarter'], df['price'], marker='o', label=ward)
        plt.xticks(rotation=90)
        plt.title("House Price Trends by Ward")
        plt.xlabel("Quarter")
        plt.ylabel("Price (£)")
        plt.legend()
        st.pyplot(plt)
    else:
        st.warning("Please select at least one ward to visualize.")


# Visualisation: Cherwell Wards Bar Chart
st.subheader("Cherwell Wards Visualisation")
# Get Cherwell wards with data from 2013 onward
cherwell_wards = pd.read_sql_query("""
    SELECT DISTINCT D.ward_name 
    FROM HousePrice HP
    JOIN District D ON HP.ward_id = D.ward_id
    WHERE HP.year >= 2013 AND D.district_name = 'Cherwell'
    ORDER BY D.ward_name
""", sqlite3.connect(db_path))['ward_name'].tolist()

# Multi-select for user
selected_cherwell_wards = st.multiselect("Select one or more Cherwell wards:", cherwell_wards)

if st.button("Show Cherwell Bar Chart"):
    if selected_cherwell_wards:
        data = pd.DataFrame()
        conn = sqlite3.connect(db_path)
        for ward in selected_cherwell_wards:
            df = pd.read_sql_query("""
                SELECT HP.price, D.ward_name
                FROM HousePrice HP
                JOIN District D ON HP.ward_id = D.ward_id
                WHERE D.ward_name = ? AND D.district_name = 'Cherwell' AND HP.year >= 2013
            """, conn, params=(ward,))
            df['Ward'] = ward
            data = pd.concat([data, df])
        if not data.empty:
            avg_prices = data.groupby("Ward")["price"].mean()
            avg_prices.plot(kind='bar', title="Average House Prices in Cherwell Wards")
            plt.ylabel("Price (£)")
            plt.xlabel("Ward")
            st.pyplot(plt)
        else:
            st.warning("No price data found for the selected wards.")
    else:
        st.warning("Please select at least one ward.")