# SortMyImages
Small Qt based image sorting utility. Groups images from a source directory based on their EXIF recording date.

## Usage
Install required packages using  "pip install -r requirements.txt". After that run sortmyimages.py
Select the source directory. The tool will then list the images with EXIF information located in the directory.
After selecting the output directory, you may select a custom separator character for the directory names.
Upon clicking _Organize_, the program will sort the listed images based on their EXIF recording date. One directory for each date is created, existing files are not overwritten. Found images are copied not moved.
