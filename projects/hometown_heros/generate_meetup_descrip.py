import csv
from datetime import datetime
from AppKit import NSPasteboard, NSStringPboardType, NSHTMLPboardType

def format_time(time_str):
    # Convert time format from "1:45-2:15" to "1:45 PM - 2:15 PM"
    try:
        start, end = time_str.split('-')
        start_time = datetime.strptime(start.strip(), '%I:%M')
        end_time = datetime.strptime(end.strip(), '%I:%M')
        return f"{start_time.strftime('%I:%M PM')} - {end_time.strftime('%I:%M PM')}"
    except:
        return time_str

def format_speaker_info(row):
    speakers = []
    if row['Presenter']:
        speaker_info = f"<b>{row['Presenter']}</b>"
        if row['Affiliation']:
            speaker_info += f", {row['Affiliation']}"
        if row['Job Title (optional)']:
            speaker_info += f" ({row['Job Title (optional)']})"
        speakers.append(speaker_info)
    
    if row['Second Presenter']:
        speaker_info = f"<b>{row['Second Presenter']}</b>"
        if row['Second Presenter Affiliation']:
            speaker_info += f", {row['Second Presenter Affiliation']}"
        if row['Second Presenter Job Title']:
            speaker_info += f" ({row['Second Presenter Job Title']})"
        speakers.append(speaker_info)
    
    return " and ".join(speakers)

def generate_html(csv_file):
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        talks = list(reader)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; }
            .talk { margin-bottom: 2em; }
            .speaker-bio { margin-bottom: 1.5em; }
        </style>
    </head>
    <body>
    """
    

    # First section: Talks
    html += "<p><b>TALK SCHEDULE</b></p>"
    for talk in talks:
        if not talk['Talk Title']:  # Skip empty entries
            continue
            
        html += f"""
        <div class="talk">
            <p><b><i>{talk['Talk Title']}</i></b></p>
            <p><b>Time:</b> {format_time(talk['Timing'])}</p>
            <p><b>Speaker{'s' if talk['Second Presenter'] else ''}:</b> {format_speaker_info(talk)}</p>
        """
        
        if talk['Talk Summary']:
            # ADD NEW LINE
            html += "<br>"
            html += f"<p>{talk['Talk Summary']}</p>"
        
        html += "</div>"
        html += "<br>"
    
    # Second section: Speaker Bios
    html += "<p><b>Speaker Bios</b></p>"
    for talk in talks:
        if not talk['Talk Title']:  # Skip empty entries
            continue
            
        if talk['Second Presenter'] and talk['Second Presenter Bio'] and talk['Second Presenter Bio'].strip():
            html += f"""
            <div class="speaker-bio">
                <p><b>{talk['Presenter']}</b></p>
                <p>{talk['Presenter Bio']}</p>
            </div>
            <div class="speaker-bio">
                <p><b>{talk['Second Presenter']}</b></p>
                <p>{talk['Second Presenter Bio']}</p>
            </div>
            """
        elif talk['Presenter'] and talk['Presenter Bio']:
            html += f"""
            <div class="speaker-bio">
                <p><b>{talk['Presenter']}</b></p>
                <p>{talk['Presenter Bio']}</p>
            </div>
            """
        html += "<br>"
    
    html += """
    </body>
    </html>
    """
    return html

def copy_to_clipboard(html_content):
    pb = NSPasteboard.generalPasteboard()
    pb.clearContents()
    pb.setString_forType_(html_content, NSHTMLPboardType)
    pb.setString_forType_(html_content, NSStringPboardType)

if __name__ == "__main__":
    html_content = generate_html('pycon/sheet.csv')
    copy_to_clipboard(html_content)
    print("Content has been copied to clipboard with formatting. You can now paste it into Google Docs.")
