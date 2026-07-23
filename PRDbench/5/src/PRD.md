### Product Requirements Template and Automated Generation Tool PRD (Product Requirement Document)

#### 1. Requirements Overview
This tool aims to implement a complete workflow from product requirements template creation to automated generation of product documentation based on templates through command-line interaction. Users can first define structured requirements templates containing image resource specifications and product feature requirements, then upload/specify image resources conforming to the templates. The system will automatically extract image features (such as dominant colors, style tags) and combine them with template information to generate standardized product PRD documents. The tool must integrate image processing, feature engineering, and document generation capabilities to ensure outputs comply with project management standards and product development requirements. Additionally, relevant README files and unit tests should be provided.

#### 2. Basic Functional Requirements

##### 2.1 Product Requirements Template Generation Module

- **Template Fields**: Include the following mandatory fields:
  - Basic Information (Product Name, Target Users)
  - Image Resource Specifications (Source Type: Local Path; Allowed File Types: JPG/PNG/jpeg/WebP)
  - Product Feature Requirements (Style Keywords: e.g., "Minimalism", "Retro Style")

- **Template Validation and Saving**: Validate user input for field completeness (mandatory fields are not empty) and file type validity (MIME type check). Upon successful validation, save in JSON format to the `src/templates/` directory, supporting template naming and overwrite confirmation.

##### 2.2 Image Resource Processing Module

- **Resource Import and Validation**: Users can input local image paths, with automatic system validation of:
  - Source type matching with "Image Resource Specifications-Source Type" in the template
  - File type inclusion in the template's allowed list (verify actual type by reading file header bytes to prevent extension spoofing)

- **Image Preprocessing**: Perform standardized processing on validated images, including:
  - Format conversion (uniformly convert to the template-specified preferred file type)
  - Metadata cleaning (remove sensitive data such as location information from EXIF data)

##### 2.3 Product Feature Extraction Module

- **Visual Feature Extraction**: Based on preprocessed images, implement the following feature extraction using OpenCV:
  - Dominant color analysis: Convert RGB color space to HSV space, use K-means clustering algorithm (k=5) to extract the top 3 dominant colors, output color values (HEX format) and proportions
  - Texture feature extraction: Calculate the image's LBP (Local Binary Pattern) histogram to generate "fine/coarse" texture tags

- **Style Description Generation**: Users need to input a large language model API key (e.g., OpenAI API Key). The system calls the API and inputs:
  - "Style Keywords"
  - Extracted dominant colors and texture tags
  - Generate product visual style description text conforming to the AIDA model (Attention-Interest-Desire-Action), limited to 200 words
  - Users may choose to input "skip" to bypass the API call, in which case the style description section will display "Style description not generated".

##### 2.4 Product PRD Document Generation Module

- **Document Structure Integration**: Generate Markdown-format PRD documents according to the following fixed structure:
  - Product Overview (from template basic information)
  - Image Resource Specifications (including processed image paths)
  - Core Feature Description (visual feature data + style description text)
  - Development Schedule Suggestions (based on Critical Path Method CPM, splitting into "image processing-feature extraction-document generation" three nodes, estimate time consumption for each node and total cycle)

**Document Output**: Support specifying the output path and file name (if not specified, use a timestamp as the file name), with the format as Markdown. The program displays "Document generation completed, path: [user-specified path]".

##### 2.5 Command-Line Interaction and Validation Module

**Menu Navigation**: Display main menu after tool startup, supporting user selection of:
  1. Create/Edit requirements template
  2. Generate product PRD based on template
  3. Exit tool

- **Input Validation**: Perform legality validation on all user inputs, including:
  - Path/URL format (local paths require file existence verification, URLs require HTTP response status code 200 verification)
  - API key format (e.g., OpenAI key must match ^sk-[A-Za-z0-9]{48}$ regular expression)
  - Numeric inputs (e.g., k-means cluster number) must be positive integers

- **Error Handling**: When input errors occur (e.g., "Unable to find image in this local path", "API key format incorrect", "Template name cannot be empty"), display prompts to the user, allow re-entry, and prevent program crashes. Specific error scenarios include:
  - Invalid menu option (not a number between 1-3)
  - Nonexistent file path
  - File type does not meet requirements
  - Incorrect API key format
  - Mandatory field left blank
  - Template file does not exist or has a format error
