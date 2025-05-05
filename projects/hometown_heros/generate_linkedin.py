outro = """
👉 Join us in cheering them on at PyCon US!
 📅 Hometown Heroes Hatchery | Saturday, May 17
 📍 David L. Lawrence Convention Center Room 317 Pittsburgh, PA 
#PyConUS2025 #PyDataPittsburgh #HometownHeroes #PythonCommunity #PittsburghTech
"""
doubl_speaker_post ="""{intro}

 🧠 {speaker_name} ({organization}) and {co_speaker_name} ({co_organization})
 🎙️ Talk title: "{talk_title}"
 ⏰ Saturday, May 17, {start_time} PM
{outro}
"""

single_speaker_post ="""{intro}

 🧠 {speaker_name} ({organization})
 🎙️ Talk title: "{talk_title}"
 ⏰ Saturday, May 17, {start_time} PM
{outro}
"""

import pandas as pd
import os
df = pd.read_csv("data/sheet.csv")

folder = "artifacts/linkedin_posts"
os.makedirs(folder, exist_ok=True)
for _, row in df.iterrows():
    with open(f"{folder}/{row['linkedin_post_date']}_{'_'.join(row['Talk Title'].lower().split(' ')[:2])}_{row['Presenter'].lower().replace(' ', '_')}_linkedin_post.txt", "w") as f:
        
        if pd.notna(row["Second Presenter"]):
            post_text = doubl_speaker_post.format(intro=row["intro"], speaker_name=row["Presenter"].strip(), co_speaker_name=row["Second Presenter"].strip(), job_title=row["Job Title (optional)"], organization=row["Affiliation"], co_job_title=row["Second Presenter Job Title"], co_organization=row["Second Presenter Affiliation"], talk_title=row["Talk Title"].strip(), start_time=row["Timing"], outro=outro)
        else:
            post_text = single_speaker_post.format(intro=row["intro"], speaker_name=row["Presenter"].strip(), job_title=row["Job Title (optional)"], organization=row["Affiliation"], talk_title=row["Talk Title"].strip(), start_time=row["Timing"], outro=outro)
        f.write(post_text)



