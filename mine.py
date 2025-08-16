import pandas as pd 
import altair as alt 
import streamlit as st 

# st.title("AirCrashes Report Analysis (1908 - 2024)")

air = pd.read_excel("Cleaned_aircrashes_dataset.xlsx")

# st.dataframe(air)

air['Year'] = air['Date'].dt.year
air = air.rename(columns={
    "Country Only": "Country",
    "decade": "Decade"
})

filters = {
"Quarter": air['Quarter'].unique(),
"Country" : air["Country"].unique(),
"Continent" : air['Continent'].unique(),
"Decade" : air["Decade"].unique(),
"Aircraft Category" : air['Aircraft Category'].unique(),
"Year": air['Year'].unique()

}

selected_filters = {}

for key, options in filters.items():
    selected_filters[key] = st.sidebar.multiselect(key, options)

filtered_air = air.copy()

for key, selected_values in selected_filters.items():
    if selected_values:
        filtered_air = filtered_air[filtered_air[key].isin(selected_values)]

# st.dataframe(filtered_air)


Total_People_aboard = filtered_air['Aboard'].sum()
Total_Air_Fatalities = filtered_air['Fatalities (air)'].sum()
Total_Ground_Cases = filtered_air['Ground'].sum()
Countries = filtered_air['Country'].nunique()
Aircraft_Manufacturers = filtered_air['Aircraft Manufacturer'].nunique()
Total_survivors = (filtered_air['Aboard'] - filtered_air['Fatalities (air)']).sum()
Total_deaths = filtered_air['Fatalities (air)'].sum() + filtered_air['Ground'].sum()

# Inject custom CSS for styling and fade-in animation
st.markdown("""
<style>
.section {
    font-size: 18px;
    line-height: 1.6;
    font-style: italic;
    color: #333333;
    background-color: #f9f9f9;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
    animation: fadeIn 1.5s ease-in-out;
}

.section h2 {
    color: #1f77b4;
    font-style: normal;
}

.section strong {
    color: #e63946;
}

@keyframes fadeIn {
    0% {opacity: 0; transform: translateY(20px);}
    100% {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# Dashboard Title
st.markdown("<h1 style='color:#1f77b4; text-align:center;'>✈ Aircraft Safety Insights Report</h1>", unsafe_allow_html=True)

# Introduction
st.markdown("""
<div class='section'>
<h2>📌 Introduction</h2>
Welcome to the <strong>Aircraft Safety and Risk Analysis Dashboard</strong>. This report provides key insights into aviation safety trends, operational risks, and manufacturer performance over time. My goal is to help HR and safety teams make informed decisions regarding <em>crew deployment, training, and risk management strategies</em>.
</div>
""", unsafe_allow_html=True)


st.write("### AirCrashes Analysis Overview")

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    st.metric("Total People Aboard: ", f"{Total_People_aboard:,.0f}")
with col2:
    st.metric("Total Air Fatalities: ", f"{Total_Air_Fatalities:,.0f}")
with col3:
    st.metric("Total Ground Cases: ", f"{Total_Ground_Cases:,.0f}")
with col4:
    st.metric("Countries: ", Countries)
with col5:
    st.metric("Aircraft Manufacturers", Aircraft_Manufacturers)
with col6:
    st.metric("Total Survivors: ", f"{Total_survivors:,.0f}")
with col7:
    st.metric("Total Deaths: ", f"{Total_deaths:,.0f}")

st.write("### Insights and Analysis Findings")

# Section 1
st.markdown("""
<div class='section'>
<h2>1️⃣ Understanding Seasonal Risk Patterns</h2>
I began by examining <strong>which quarter of the year experiences the highest number of aircraft incidents</strong>. Seasonal trends help us anticipate peak-risk periods and allocate safety resources effectively.
</div>
""", unsafe_allow_html=True)

st.write("#### 1. Which quarter of the year experiences the highest number of aircraft incidents?")

quarter_cases = filtered_air['Quarter'].value_counts().reset_index()
quarter_cases.columns = ['Quarter', 'Crash_Count']

# st.dataframe(quarter_cases)

chart1 = alt.Chart(quarter_cases).mark_bar().encode(
    x=alt.X('Quarter:N', sort=['Q1', 'Q2', 'Q3', 'Q4'], title='Quarter'),
    y=alt.Y('Crash_Count:Q', title='Number of Crashes'),
    color=alt.Color('Quarter:N', legend=None)
).properties(
    width=600,
    height=400,
    title='Aircraft Crash Cases per Quarter'
)

st.altair_chart(chart1, use_container_width=True)

# Section 2
st.markdown("""
<div class='section'>
<h2>2️⃣ Identifying High-Risk Regions</h2>
Next, I explored <strong>the top 10 countries with the highest passenger fatalities</strong> and <strong>continents with the most ground fatalities</strong>. These insights guide HR in assessing regional safety concerns, managing crew assignments, and designing location-specific safety programs.
</div>
""", unsafe_allow_html=True)

st.write("#### 2. Which 10 countries have recorded the highest number of passenger fatalities over time?")

exclude_list = ['Unknown', 'N/A']

# First, filter
air = air[air['Country'].isin(filtered_air['Country'])]

# Then, do the groupby logic
top_countries = (
    air.loc[~air['Country'].isin(exclude_list)]  # Exclude 'Unknown' and 'N/A'
       .groupby('Country')['Fatalities (air)']
       .sum()
       .sort_values(ascending=False)
       .head(10)
       .reset_index()
)

# Show in Streamlit
# st.dataframe(top_countries)

chart = alt.Chart(data=top_countries).mark_bar().encode(
    x=alt.X('Fatalities (air):Q', title='Fatalities (air)'),
    y=alt.Y('Country:N', sort='-x', title='Country'),
    color=alt.Color('Country:N', legend=None),
    tooltip=['Country:N', 'Fatalities (air):Q']
).properties(
    width=700,
    height=400,
    title='Top 10 Countries by Air Fatalities'
)

# Display chart in Streamlit
st.altair_chart(chart, use_container_width=True)

st.write("#### 3. Which continents have recorded the most ground fatalities during crashes?")

continent_ground_fatalities = (
    filtered_air[filtered_air['Continent'] != 'Unknown']
    .groupby('Continent')['Ground']
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
continent_ground_fatalities.columns = ['Continent', 'Ground_Fatalities']

# st.dataframe(continent_ground_fatalities)

chart = alt.Chart(continent_ground_fatalities).mark_bar().encode(
    x=alt.X('Ground_Fatalities:Q', title='Ground Fatalities'),
    y=alt.Y('Continent:N', sort='-x', title='Continent'),
    color=alt.Color('Continent:N', legend=None),
    tooltip=['Continent:N', 'Ground_Fatalities:Q']
).properties(
    width=600,
    height=400,
    title='Ground Fatalities by Continent'
)

# Display chart
st.altair_chart(chart, use_container_width=True)

# Section 3
st.markdown("""
<div class='section'>
<h2>3️⃣ Historical Safety Improvements</h2>
I analyzed <strong>how survival rates versus death rates have changed across decades</strong>, alongside <strong>the trend of average fatalities per year</strong>. This historical perspective shows whether safety measures have improved industry outcomes over time.
</div>
""", unsafe_allow_html=True)

st.write("#### 4. How has the survival rate compared to the death rate changed across different decades?")

survival_trend = filtered_air.groupby('Decade').apply(
    lambda x: pd.Series({
        'Total_Aboard': x['Aboard'].sum(),
        'Total_Fatalities': x['Fatalities (air)'].sum()
    }),
    include_groups=False
).reset_index()


survival_trend['Survival_Rate'] = (survival_trend['Total_Aboard'] - survival_trend['Total_Fatalities']) / survival_trend['Total_Aboard']
survival_trend['Death_Rate'] = survival_trend['Total_Fatalities'] / survival_trend['Total_Aboard']

trend_long = survival_trend.melt(id_vars='Decade', value_vars=['Survival_Rate', 'Death_Rate'],
                                 var_name='Metric', value_name='Rate')

# st.dataframe(survival_trend)

chart = alt.Chart(trend_long).mark_line(point=True).encode(
    x=alt.X('Decade:N', title='Decade', sort=None),
    y=alt.Y('Rate:Q', title='Rate'),
    color=alt.Color('Metric:N', title='Metric'),
    tooltip=['Decade:N', 'Metric:N', alt.Tooltip('Rate:Q', format='.2%')]
).properties(
    width=700,
    height=400,
    title='Survival vs Death Rates Over Decades'
)

# Display chart
st.altair_chart(chart, use_container_width=True)

st.write("#### 5. What is the trend of average fatalities per year in the aviation industry?")

avg_fatalities_by_year = filtered_air.groupby(air['Date'].dt.year)['Fatalities (air)'].mean().reset_index()
avg_fatalities_by_year.columns = ['Year', 'Avg_Fatalities']

# st.dataframe(avg_fatalities_by_year)

chart = alt.Chart(avg_fatalities_by_year).mark_line(point=True).encode(
    x=alt.X('Year:O', title='Year'),
    y=alt.Y('Avg_Fatalities:Q', title='Average Fatalities per Crash'),
    tooltip=['Year:O', alt.Tooltip('Avg_Fatalities:Q', format=',.2f')]
).properties(
    width=700,
    height=400,
    title='Yearly Trend of Average Fatalities per Crash'
)

# Display chart
st.altair_chart(chart, use_container_width=True)

# Section 4
st.markdown("""
<div class='section'>
<h2>4️⃣ Multi-Dimensional Impact Across Decades</h2>
I compared <strong>ground fatalities, in-air fatalities, and people aboard across decades</strong>. This gives us a holistic view of how different aspects of crash severity have evolved, informing HR on whether current operational practices are reducing overall impact.
</div>
""", unsafe_allow_html=True)

st.write("#### 6. How do ground fatalities, in-air fatalities, and people aboard compare across decades?")

ground_fatalities_decade = filtered_air.groupby('Decade').agg({
    'Ground': 'sum',
    'Fatalities (air)': 'sum',
    'Aboard': 'sum'
}).reset_index()

# st.dataframe(ground_fatalities_decade)

# Melt the dataframe for Altair
air_melted = ground_fatalities_decade.melt(id_vars='Decade', value_vars=['Ground', 'Fatalities (air)', 'Aboard'],
                                          var_name='Metric', value_name='Count')

line_chart = alt.Chart(air_melted).mark_line(point=True).encode(
    x=alt.X('Decade:N', title='Decade'),
    y=alt.Y('Count:Q', title='Count'),
    color=alt.Color('Metric:N', title='Metric'),
    tooltip=['Decade:N', 'Metric:N', 'Count:Q']
).properties(
    width=700,
    height=400,
    title='Trend of Ground, Fatalities, and Aboard per Decade'
)

st.altair_chart(line_chart, use_container_width=True)

# Section 5
st.markdown("""
<div class='section'>
<h2>5️⃣ Operational Risk by Aircraft Category</h2>
Not all flights are equal. I investigated <strong>which aircraft categories—commercial, cargo, or private—record the highest fatalities</strong>, enabling HR to identify which operational types require enhanced training and emergency preparedness.
</div>
""", unsafe_allow_html=True)

st.write("#### 7. Which aircraft categories record the highest number of fatalities?")

category_deaths = (
    filtered_air.groupby('Aircraft Category')['Fatalities (air)']
       .sum()
       .sort_values(ascending=False)
       .reset_index()
)
category_deaths.columns = ['Category', 'Total_Fatalities']
category_deaths['Percentage'] = (category_deaths['Total_Fatalities'] / category_deaths['Total_Fatalities'].sum()) * 100

# st.dataframe(category_deaths)

chart = alt.Chart(category_deaths).mark_arc(innerRadius=70).encode(
    theta=alt.Theta(field='Total_Fatalities', type='quantitative'),
    color=alt.Color(field='Category', type='nominal', legend=alt.Legend(title="Aircraft Category")),
    tooltip=['Category:N', 'Total_Fatalities:Q', alt.Tooltip('Percentage:Q', format='.2f')]
).properties(
    width=500,
    height=500,
    title='Fatalities by Aircraft Category'
)

# Display chart
st.altair_chart(chart, use_container_width=True)

# Section 6
st.markdown("""
<div class='section'>
<h2>6️⃣ Manufacturer-Level Risk Analysis</h2>
I revealed <strong>which aircraft manufacturers have the highest total fatalities and how their survival and death rates compare</strong>, followed by <strong>which manufacturers tend to have the most severe crashes on average</strong>.
</div>
""", unsafe_allow_html=True)

st.write("#### 8. Which aircraft manufacturers have the highest total fatalities, and how do their survival and death rates compare?")

manufacturer_stats = filtered_air.groupby('Aircraft Manufacturer').agg(
    Total_Aboard=('Aboard', 'sum'),
    Total_Fatalities=('Fatalities (air)', 'sum')
).reset_index()

manufacturer_stats['Survival_Rate'] = (manufacturer_stats['Total_Aboard'] - manufacturer_stats['Total_Fatalities']) / manufacturer_stats['Total_Aboard']
manufacturer_stats['Death_Rate'] = manufacturer_stats['Total_Fatalities'] / manufacturer_stats['Total_Aboard']

top20_manufacturers = manufacturer_stats.sort_values(by='Total_Fatalities', ascending=False).head(20)
top20_long = top20_manufacturers.melt(id_vars='Aircraft Manufacturer', value_vars=['Survival_Rate', 'Death_Rate'],
                                      var_name='Metric', value_name='Rate')

# st.dataframe(manufacturer_stats)

# Streamlit title
# st.subheader("Top 20 Aircraft Manufacturers: Survival vs Death Rates")

# Altair stacked bar chart
chart = alt.Chart(top20_long).mark_bar().encode(
    x=alt.X('Rate:Q', stack='normalize', title='Rate'),
    y=alt.Y('Aircraft Manufacturer:N', sort='-x', title='Manufacturer'),
    color=alt.Color('Metric:N', title='Metric', scale=alt.Scale(domain=['Survival_Rate', 'Death_Rate'], range=['#2ecc71', '#e74c3c'])),
    tooltip=['Aircraft Manufacturer:N', 'Metric:N', alt.Tooltip('Rate:Q', format='.2%')]
).properties(
    width=700,
    height=500,
    title='Survival vs Death Rates for Top 20 Manufacturers'
)

# Display chart
st.altair_chart(chart, use_container_width=True)

st.write("#### 9. Which aircraft manufacturers have the most severe crashes on average (in terms of fatalities per crash)?")

manufacturer_severity = filtered_air.groupby('Aircraft Manufacturer')['Fatalities (air)'].mean().sort_values(ascending=False).head(20).reset_index()
manufacturer_severity.columns = ['Manufacturer', 'Avg_Fatalities']

# st.dataframe(manufacturer_severity)

chart = alt.Chart(manufacturer_severity).mark_bar().encode(
    x=alt.X('Avg_Fatalities:Q', title='Average Fatalities per Crash'),
    y=alt.Y('Manufacturer:N', sort='-x', title='Manufacturer'),
    color=alt.Color('Manufacturer:N', legend=None),
    tooltip=['Manufacturer:N', alt.Tooltip('Avg_Fatalities:Q', format=',.2f')]
).properties(
    width=700,
    height=500,
    title='Top 20 Manufacturers by Average Fatalities per Crash'
)

# Display chart
st.altair_chart(chart, use_container_width=True)

# Section 7
st.markdown("""
<div class='section'>
<h2>7️⃣ Improvement Over Time</h2>
Finally, I highlighted <strong>which manufacturers have shown the most improvement in survival rates over time</strong>, showcasing progress in aviation safety and potential preferred partners for future operations.
</div>
""", unsafe_allow_html=True)

st.write("#### 10. Which aircraft manufacturers have shown the most improvement in survival rates over time?")

# Calculate survival rate by manufacturer and decade
manufacturer_trend = filtered_air.groupby(['Aircraft Manufacturer', 'Decade']).apply(
    lambda x: pd.Series({
        'Total_Aboard': x['Aboard'].sum(),
        'Total_Fatalities': x['Fatalities (air)'].sum()
    }),
    include_groups=False
).reset_index()

manufacturer_trend['Survival_Rate'] = (
    (manufacturer_trend['Total_Aboard'] - manufacturer_trend['Total_Fatalities']) /
    manufacturer_trend['Total_Aboard']
)

# Compute improvement: latest decade survival rate - earliest decade survival rate
improvement = (
    manufacturer_trend.groupby('Aircraft Manufacturer')
    .agg(
        First_Survival_Rate=('Survival_Rate', 'first'),
        Last_Survival_Rate=('Survival_Rate', 'last')
    )
    .assign(Improvement=lambda df: df['Last_Survival_Rate'] - df['First_Survival_Rate'])
    .sort_values(by='Improvement', ascending=False)
    .reset_index()
)

# Get top 10 manufacturers with the most improvement
top_improvers = improvement.head(20)
# st.dataframe(top_improvers)

chart = alt.Chart(top_improvers).mark_bar().encode(
    x=alt.X('Aircraft Manufacturer:N', sort='-y', title='Manufacturer'),
    y=alt.Y('Improvement:Q', title='Improvement in Survival Rate'),
    color=alt.Color('Improvement:Q', scale=alt.Scale(scheme='greens')),
    tooltip=['Aircraft Manufacturer', 'First_Survival_Rate', 'Last_Survival_Rate', 'Improvement']
).properties(
    title='Top 20 Aircraft Manufacturers with Most Improvement in Survival Rate',
    width=700,
    height=400
)

st.altair_chart(chart, use_container_width=True)

from datetime import datetime

# =========================
# STYLES (clean + animated)
# =========================
st.markdown("""
<style>
:root{
  --brand:#1f77b4; --ink:#1f2937; --muted:#6b7280; --bg:#f8fafc; --card:#ffffff; --ok:#16a34a; --warn:#e11d48;
}
.section-title {
  font-size: 1.4rem; font-weight: 700; color: var(--brand); margin: 0.2rem 0 0.6rem 0;
}
.subtle { color: var(--muted); font-size: 0.95rem; }
.card {
  background: var(--card); border-radius: 14px; padding: 18px 18px;
  box-shadow: 0 6px 18px rgba(2,6,23,0.06); border:1px solid #eef2f7;
  animation: fadeInUp 600ms ease; margin-bottom: 14px;
}
.card h4 { margin: 0 0 0.5rem 0; color: var(--ink); }
.card ul { margin: 0.2rem 0 0 1.1rem; }
.badge { display:inline-block; padding: 2px 8px; border-radius: 999px; background: #eef6ff; color: var(--brand); font-size: 0.8rem; font-weight:600; }
.kicker { font-size: 0.95rem; color: var(--muted); margin-bottom: 0.6rem; font-style: italic; }
.hr { height:1px; background:#eef2f7; border:0; margin: 10px 0 16px 0; }
@keyframes fadeInUp { from {opacity:0; transform: translateY(8px);} to {opacity:1; transform: translateY(0);} }
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("## 📌 Executive Takeaways")
st.markdown(
    f"<div class='subtle'>Concise findings, likely causes, and actionable recommendations for HR & Safety leadership. "
    f"Last updated: <strong>{datetime.now().strftime('%Y-%m-%d %H:%M')}</strong></div>",
    unsafe_allow_html=True
)
st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# =========================
# FINDINGS + CAUSES
# =========================
st.markdown("<div class='section-title'>Findings & Potential Causes</div>", unsafe_allow_html=True)
left, right = st.columns(2)

with left:
    st.markdown("""
    <div class="card">
      <span class="badge">High-Risk Countries</span>
      <div class="kicker">Where fatalities concentrate</div>
      <ul>
        <li><strong>United States, Russia, Brazil, Colombia, France, India, Indonesia, China, UK, Spain</strong> show the highest passenger fatalities.</li>
      </ul>
      <div class="kicker">Likely drivers</div>
      <ul>
        <li>High traffic density, complex weather, varied infrastructure quality, and challenging terrain/routes.</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
      <span class="badge">Ground Fatalities Spike (2000s)</span>
      <div class="kicker">Elevated non-airborne impact</div>
      <ul>
        <li>Unusual increase in ground casualties during the 2000s.</li>
      </ul>
      <div class="kicker">Likely drivers</div>
      <ul>
        <li>Runway incursions, on-ground collisions, fueling/handling incidents, perimeter security gaps.</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown("""
    <div class="card">
      <span class="badge">Trend Over Decades</span>
      <div class="kicker">Overall safety improving with a temporary spike</div>
      <ul>
        <li>Death rates declined from the late 1960s to early 2000s, spiked in the 2010s, then improved markedly in the 2020s.</li>
      </ul>
      <div class="kicker">Likely drivers</div>
      <ul>
        <li>Regulatory upgrades, avionics/airframe advances, variable compliance in high-growth markets, exposure effects.</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
      <span class="badge">Risk by Category & Manufacturer</span>
      <div class="kicker">Where operational exposure is highest</div>
      <ul>
        <li><strong>Commercial jets, military, regional, helicopters, general aviation</strong> have the highest fatalities.</li>
        <li>Higher crash severity (historically) among <strong>Airbus, McDonnell, Mil Moscow, Tupolev, Boeing, Bombardier, Sikorsky, Bristol, Sud Aviation</strong>.</li>
        <li>Notable survival improvements over time in <strong>Mikoyan-Gurevich, Transall, Aeronautical Macchi, Consolidated Aircraft, Tupolev</strong>.</li>
      </ul>
      <div class="kicker">Likely drivers</div>
      <ul>
        <li>Operational complexity, mission profiles, legacy fleets, safety retrofits and training quality.</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# =========================
# RECOMMENDATIONS
# =========================
st.markdown("<div class='section-title'>Actionable Recommendations</div>", unsafe_allow_html=True)

rec_cards = [
    {
        "title":"Targeted Training & Recurrent Drills",
        "desc":"Prioritize emergency response, CRM, and terrain/weather procedures for crews operating in high-risk regions and categories (commercial, military, helicopters, regional).",
        "tone":"ok"
    },
    {
        "title":"Airport & Ground Safety Audits",
        "desc":"Partner with operators/authorities to audit runway incursion controls, apron procedures, and perimeter security—especially at airports linked to the 2000s ground spike.",
        "tone":"ok"
    },
    {
        "title":"Risk-Based Crew Assignment",
        "desc":"Deploy the most experienced flight/maintenance crews on routes, seasons, and aircraft categories with elevated risk; enforce pre-departure risk briefings.",
        "tone":"ok"
    },
    {
        "title":"Fleet & Partner Due Diligence",
        "desc":"Use manufacturer trend data (severity & survival improvement) in procurement/lease decisions; favor platforms and partners with clear safety gains.",
        "tone":"ok"
    },
    {
        "title":"Continuous Monitoring Dashboard",
        "desc":"Maintain live KPIs by region, category, and manufacturer (survival, fatalities, ground events). Trigger alerts on adverse shifts to accelerate interventions.",
        "tone":"ok"
    },
]

# Render recs as cards
for r in rec_cards:
    st.markdown(
        f"""
        <div class="card">
          <h4>✅ {r['title']}</h4>
          <div class="subtle">{r['desc']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# DOWNLOADS (CSV + Markdown)
# =========================
findings_md = """# Executive Takeaways

## Findings & Potential Causes
- **High-Risk Countries:** United States, Russia, Brazil, Colombia, France, India, Indonesia, China, UK, Spain.  
  *Likely causes:* traffic density, complex weather, infrastructure variance, terrain/routes.
- **Trend Over Decades:** Death rates declined (late 1960s–early 2000s), spiked in 2010s, improved in 2020s.  
  *Likely causes:* regulatory upgrades, avionics, variable compliance, exposure.
- **Ground Fatalities (2000s):** Unusual spike in on-ground casualties.  
  *Likely causes:* runway incursions, ground collisions, handling incidents, security gaps.
- **Risk by Category & Manufacturer:** Highest exposure in commercial, military, regional, helicopters, GA. Historical severity higher among Airbus, McDonnell, Mil Moscow, Tupolev, Boeing, Bombardier, Sikorsky, Bristol, Sud Aviation. Improvements noted for Mikoyan-Gurevich, Transall, Aeronautical Macchi, Consolidated Aircraft, Tupolev.

## Recommendations
1. Targeted Training & Recurrent Drills.
2. Airport & Ground Safety Audits.
3. Risk-Based Crew Assignment.
4. Fleet & Partner Due Diligence.
5. Continuous Monitoring Dashboard.

_Last updated: {ts}_
""".format(ts=datetime.now().strftime("%Y-%m-%d %H:%M"))

# CSV: two-column summary to share quickly
csv_rows = [
    ["High-Risk Countries", "US, Russia, Brazil, Colombia, France, India, Indonesia, China, UK, Spain"],
    ["Trend Over Decades", "Decline (late 1960s–2000s), spike (2010s), improvement (2020s)"],
    ["Ground Fatalities (2000s)", "Spike; runway/apron/security vulnerabilities"],
    ["Risk by Category", "Commercial, military, regional, helicopters, GA"],
    ["Higher Severity (Historical)", "Airbus, McDonnell, Mil Moscow, Tupolev, Boeing, Bombardier, Sikorsky, Bristol, Sud Aviation"],
    ["Improvement in Survival", "Mikoyan-Gurevich, Transall, Aeronautical Macchi, Consolidated Aircraft, Tupolev"],
    ["Key Actions",
     "Training; Ground audits; Risk-based crew; Due diligence; Continuous monitoring"],
]
df_takeaway = pd.DataFrame(csv_rows, columns=["Topic", "Summary"])

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
dl_col1, dl_col2 = st.columns([1,1])
with dl_col1:
    st.download_button(
        label="📥 Download Executive Takeaways (Markdown)",
        data=findings_md.encode("utf-8"),
        file_name="executive_takeaways.md",
        mime="text/markdown"
    )
with dl_col2:
    st.download_button(
        label="📊 Download Summary Table (CSV)",
        data=df_takeaway.to_csv(index=False).encode("utf-8"),
        file_name="executive_takeaways.csv",
        mime="text/csv"
    )

# =========================
# OPTIONAL: Notes / Assumptions
# =========================
with st.expander("Notes & Assumptions"):
    st.write("""
- Findings reflect patterns in the provided dataset; results may vary with additional data or reclassification.
- Manufacturer severity and improvements are historical and context-dependent (fleet age, mission, geography).
- Recommendations should complement regulator/ICAO/IATA directives and operator SOPs.
    """)






