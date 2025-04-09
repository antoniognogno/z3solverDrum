import aspose.pdf as ap
import os

# Create a new PDF document
pdfDocument = ap.Document()

# Transform and bind XML
script_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the script's directory
output_file = os.path.join(script_dir, 'spartito.xml') # Creates the path, same folder
pdfDocument.bind_xml(output_file)

# Generate PDF from XML
output_file = os.path.join(script_dir, 'spartito.pdf')
pdfDocument.save(output_file)