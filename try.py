import PyPDF2

# Function to Read PDF File and return its Text
def pdfReader(pdf_path):
    try:
        with open(pdf_path, 'rb') as pdfFileObject:
            # Create a PDF reader object
            pdfReader = PyPDF2.PdfReader(pdfFileObject)
            count = len(pdfReader.pages)
            print("\nTotal Pages in pdf = ", count)
            
            c = input("Do you want to read the entire PDF? [Y]/N  :  ")
            start_page = 0
            end_page = count - 1
            
            if c.lower() == 'n':
                # User chooses to specify pages
                start_page = int(input("Enter start page number (Indexing starts from 0) :  "))
                end_page = int(input(f"Enter end page number (Less than {count}) : "))
                
                # Validate page numbers
                if start_page < 0 or start_page >= count:
                    print("\nInvalid Start page given")
                    return ""
                
                if end_page < 0 or end_page >= count:
                    print("\nInvalid End page given")
                    return ""
                
                if start_page > end_page:
                    print("\nStart page cannot be greater than end page")
                    return ""
            
            # Extract text from the specified pages
            full_text = ""
            for i in range(start_page, end_page + 1):
                page = pdfReader.pages[i]
                full_text += page.extract_text()

            return full_text

    except FileNotFoundError:
        print("Error: The file was not found.")
        return ""
    except PyPDF2.errors.PdfReadError:
        print("Error: There was an issue reading the PDF file.")
        return ""
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return ""

# Example of calling the pdfReader function
if __name__ == "__main__":
    pdf_path = input("Enter the path to the PDF file: ")
    pdf_text = pdfReader(pdf_path)
    
    if pdf_text:
        print("\nExtracted Text:\n")
        print(pdf_text)
    else:
        print("No text was extracted from the PDF.")
