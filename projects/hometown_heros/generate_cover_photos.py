import os
import jinja2
from typing import Dict, List
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image
import io
import base64
import time

PARENT_DIR = Path(__file__).parent

def generate_cover_photo(
    template_path: str,
    output_path: str,
    headshot_path: str,
    talk_title: str,
    presenter: str,
    affiliation: str,
    job_title: str = ""
) -> None:
    """
    Generate a cover photo using the HTML template.
    
    Args:
        template_path: Path to the HTML template
        output_path: Where to save the generated image
        headshot_path: Path to the speaker's headshot image
        talk_title: Title of the talk
        presenter: Name of the presenter
        affiliation: Presenter's affiliation
        job_title: Presenter's job title (optional)
    """
    # Load the template
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Create Jinja2 environment and template
    template = jinja2.Template(template_content)
    
    # Convert headshot to base64
    with open(headshot_path, 'rb') as img_file:
        headshot_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    
    # Render the template with the provided data
    html_content = template.render(
        talk_title=talk_title,
        presenter=presenter,
        affiliation=affiliation,
        job_title=job_title,
        headshot_base64=f"data:image/jpeg;base64,{headshot_base64}"
    )
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--window-size=1200,630')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Create a temporary HTML file
        temp_html = Path('temp.html')
        temp_html.write_text(html_content)
        
        # Load the HTML file
        driver.get(f'file://{temp_html.absolute()}')
        
        # Wait for fonts to load
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.fonts.ready')
        )
        
        # Additional small delay to ensure everything is rendered
        time.sleep(0.5)
        
        # Take screenshot
        screenshot = driver.get_screenshot_as_png()
        
        # Convert to PIL Image and save
        image = Image.open(io.BytesIO(screenshot))
        image.save(output_path, 'PNG', quality=100)
        
    finally:
        driver.quit()
        # Clean up temporary file
        if temp_html.exists():
            temp_html.unlink()

def generate_cover_photos(
    template_path: str,
    output_dir: str,
    headshot_dir: str,
    talks: List[Dict[str, str]]
) -> None:
    """
    Generate multiple cover photos for different talks.
    
    Args:
        template_path: Path to the HTML template
        output_dir: Directory to save generated images
        headshot_dir: Directory containing speaker headshots
        talks: List of dictionaries containing talk information
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    for talk in talks:
        headshot_path = os.path.join(headshot_dir, talk['headshot_filename'])
        output_path = os.path.join(
            output_dir,
            f"{'_'.join(talk['talk_title'].lower().split(' ')[:2])}_{talk['presenter'].lower().replace(' ', '_')}_cover.png"
        )
        
        generate_cover_photo(
            template_path=template_path,
            output_path=output_path,
            headshot_path=headshot_path,
            talk_title=talk['talk_title'],
            presenter=talk['presenter'],
            affiliation=talk['affiliation'],
            job_title=talk.get('job_title', '')
        )
        print(f"Generated cover photo for {talk['presenter']}")
    

def get_affiliation(row) -> str:
    if pd.notna(row['Job Title (optional)']) and pd.notna(row['Affiliation']):
        if len(row['Job Title (optional)']) > 30:
            return  f"{row['Job Title (optional)']}\n@ {row['Affiliation']}"
        return f"{row['Job Title (optional)']}" + f"@ {row['Affiliation']}" if row['Afilliation'] else ""
    elif pd.notna(row['Job Title (optional)']):
        return row['Job Title (optional)']
    elif pd.notna(row['Affiliation']):
        return row['Affiliation']
    else:
        return ""

if __name__ == "__main__":
    # Example usage
    template_path = PARENT_DIR / "linkedin.html"
    output_dir = PARENT_DIR / "artifacts" / "cover_photos"
    headshot_dir = PARENT_DIR / "data" / "headshots"

    import pandas as pd
    df = pd.read_csv(PARENT_DIR / "data" / "sheet.csv")
    
    talks = []
    for _, row in df.iterrows():
        if "Chris" not in row["Presenter"]:
            continue

        if pd.notna(row['headshot']):

            if pd.notna(row['Job Title (optional)']) and pd.notna(row['Affiliation']):
                if row['Affiliation'] == " ":
                    affiliation = f"{row['Job Title (optional)']}"
                else:
                    affiliation = f"{row['Job Title (optional)']} @ {row['Affiliation']}"
            elif pd.notna(row['Job Title (optional)']):
                affiliation = row['Job Title (optional)']
            elif pd.notna(row['Affiliation']):
                affiliation = row['Affiliation']
            else:
                affiliation = ""

            talks.append({
                "headshot_filename": row['headshot'],
                "talk_title": row['Talk Title'],
                "presenter": row['Presenter'],
                "affiliation": affiliation,
            })


        # do the same for all second presenters
        if pd.notna(row['Second Presenter']):
            if pd.notna(row['Second Presenter Job Title']) and pd.notna(row['Second Presenter Affiliation']):
                affiliation = f"{row['Second Presenter Job Title']} @ {row['Second Presenter Affiliation']}"
            elif pd.notna(row['Second Presenter Job Title']):
                affiliation = row['Second Presenter Job Title']
            elif pd.notna(row['Second Presenter Affiliation']):
                affiliation = row['Second Presenter Affiliation']
            else:
                affiliation = ""
            talks.append({
                "headshot_filename": row['Second Presenter Headshot'],
                "talk_title": row['Talk Title'],
                "presenter": row['Second Presenter'],
                "affiliation": affiliation,
            })


        
    # break
    generate_cover_photos(template_path, output_dir, headshot_dir, talks)
