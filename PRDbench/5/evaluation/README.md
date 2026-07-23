# Product Requirements Template and Auto-Generation Tool Documentation

## Introduction

This tool is a command-line application designed to help product teams quickly generate standardized Product Requirements Documents (PRD) through structured templates and automated processing workflows. The tool integrates image processing, feature extraction, and document generation capabilities, significantly improving the efficiency and quality of product documentation.

## Environment Setup

### System Requirements

- Python 3.7 or higher
- Windows, macOS, or Linux operating system

### Installing Dependencies

1. Clone or download the project to a local directory
2. Open a terminal or command prompt and navigate to the project root directory
3. Run the following command to install dependencies:

```bash
pip install -r src/requirements.txt
```

### Dependency Description

- `opencv-python`: For image processing and computer vision features (optional, simplified implementation available as fallback)
- `Pillow`: For image processing
- `scikit-learn`: For machine learning algorithms (optional, simplified implementation available as fallback)
- `requests`: For network requests (calling large language model APIs)

### Handling Dependency Installation Issues

On some systems (especially Windows), installing certain dependencies may encounter issues:

1. **Use a domestic mirror source**:
   ```bash
   pip install -r src/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

2. **Install only pre-compiled binary packages**:
   ```bash
   pip install -r src/requirements.txt --only-binary=all
   ```

3. **If opencv-python or scikit-learn still cannot be installed**:
   - The program has built-in simplified implementations that can run basic functions without these libraries
   - The program will automatically detect whether dependencies exist and use simplified implementations if they are missing

## Usage

### Starting the Tool

Run the following command in the project root directory to start the tool:

```bash
python src/main.py
```

### Main Features

After starting, the tool displays a main menu with the following options:

1. **Create/Edit Requirement Template**
   - Enter basic product information as prompted (product name, target users)
   - Set image resource specifications (source type, allowed file formats)
   - Define product feature requirements (style keywords, color emotion tendency)
   - Enter template name and save

2. **Generate Product PRD Based on Template**
   - Select one from saved templates
   - Provide image resource paths that meet template specifications
   - (Optional) Enter a large language model API key to generate style descriptions
   - The tool will automatically process images, extract features, and generate PRD documents

3. **Exit Tool**
   - Safely exit the program

### Detailed Operation Workflow

#### Creating a Product Requirements Template

1. Select menu item 1 to enter the template creation process
2. Enter product name and target users as prompted
3. Confirm image resource specifications (default is local path, supports JPG/PNG/WebP formats)
4. Enter style keywords (separate multiple keywords with commas)
5. Select color emotion tendency from predefined options
6. Enter template name and save

#### Generating a Product PRD Document

1. Select menu item 2 to enter the PRD generation process
2. Select a saved template from the list
3. Enter absolute paths to image files line by line (one per line, enter blank line to finish)
4. (Optional) Enter a large language model API key to generate style descriptions (enter 'skip' to skip)
5. (Optional) Enter a name for the generated document
6. The tool will automatically process images, extract features, and generate the PRD document

### Output Files

- Generated PRD documents will be saved in the `src/output/` directory in Markdown format
- Processed images will be saved in the `src/images/` directory
- Template files are saved in the `src/templates/` directory

## Technical Notes

### Image Processing Workflow

1. **Format Validation**: Verify that the image format meets template requirements
2. **Preprocessing**: Uniformly convert to the priority format specified by the template, clean metadata
3. **Feature Extraction**:
   - Use color histogram method to extract dominant colors (top 3)
   - Analyze texture features through pixel difference analysis (smooth/rough)
4. **Style Description Generation**: (Optional) Call a large language model API to generate descriptions conforming to the AIDA model

### Document Structure

Generated PRD documents contain the following sections:

1. Product Overview
2. Image Resource Specifications
3. Core Feature Description
4. Development Schedule Suggestions (based on critical path method)

## Notes

1. Image paths must be absolute paths
2. API key format must conform to OpenAI key specifications (48-character string starting with sk-)
3. The tool will automatically create necessary directories (templates, images, output)
4. Processing large numbers of images may take longer, please be patient

## Troubleshooting

### Common Issues

1. **Unable to install dependencies**
   - Ensure Python and pip are correctly installed
   - Try installing using a domestic mirror source: `pip install -r src/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
   - If a specific package cannot be installed, the program will automatically use simplified implementations

2. **Image processing failed**
   - Check if the image path is correct
   - Confirm that the image format is within the range allowed by the template
   - Ensure the image file is not occupied by another program

3. **API call failed**
   - Check if the API key format is correct
   - Confirm network connection is normal
   - Check if the API service is running normally

### Getting Help

If you encounter other issues, please check the comments in the source code or contact the developer.

## Version Information

Current version: 1.0.0
