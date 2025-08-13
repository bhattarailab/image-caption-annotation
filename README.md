## Vision Language Annotation Tool
- A simple Python script to annotate image files with descriptions.
- Opens images and their associated text side by side from a JSON file.
- Selects images from a user-selected directory.  
- Select certain region of text and mark as correct or incorrect.  

### Demo image
<img src="https://github.com/sandeshpokhrel54/Image_caption_annotation/blob/main/demos/demo1.jpeg" width="600" alt="Medical image annotation">

### Usage
You can download executable (.exe) file directly from the drive link: <a href="https://drive.google.com/drive/folders/1pqRw19suJ58Jlz7U7hzyNwBZn_0YynFG?usp=drive_link">Textannotator.exe</a>

OR

If you want to install the software locally through source code, simply do the following:
```bash
git clone https://github.com/sandeshpokhrel54/Image_caption_annotation
cd Image_caption_annotation
pip install -r requirements.txt
python caption.py
```


Then, you will be prompted to select the image folder and json file of a class.
<br>
- First Select the Image Folder
<br>
<img src="https://github.com/sandeshpokhrel54/Image_caption_annotation/blob/main/demos/select_image_class.png" width="600" alt="Select Image Folder">

- Then, select the corresponding json file
<br>
<img src="https://github.com/sandeshpokhrel54/Image_caption_annotation/blob/main/demos/select_json.png" width="600" alt="Select Json File">


#### Developed at Multi Modal Learning Lab, NAAMII,Nepal for clinicians in vision language annotation under Assistant Professor Binod Bhattarai, PhD. University of Aberdeen.
