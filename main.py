#importing required libraries
import pandas as pd
from fpdf import FPDF
import os
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt

from pyarrow import output_stream
from streamlit import exception

#step 1 read the csv file
def read_data(file_path):
    try:
        file_path = file_path.strip().strip('"')  # Clean path
        data = pd.read_csv(file_path)
        print("File loaded successfully!\n")
        print(data.head()) # Show first 5 rows
        return data
    except FileNotFoundError:
        print(" File not found. Please check the path.")
        return None
    except Exception as e:
        print(f" Error reading file: {e}")
        return None
#Analyze_data
def analyze_data(data):
    summary = {
        "Total Rows": len(data),
        "Columns": data.columns.tolist(),
        "Mean of Numeric Columns": data.select_dtypes(include='number').mean().round(2).to_dict(),
        "Missing Values": data.isnull().sum().to_dict()
    }

    print("Analysis Summary:")
    for key, value in summary.items():
        print(f"{key} : {value}")

    return summary


# adding a heatmap to show better visualisation of numeric features
def create_correlation_heatmap(data,output_image_path):
    plt.figure(figsize = (10,8))
    corr = data.select_dtypes(include='number').corr()
    sns.heatmap(corr, annot=True,fmt=".2f",cmap="coolwarm",cbar=True)
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(output_image_path)
    plt.close()



# Class to create the PDF report
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0,10,"Data Analysis Report",border=0,ln=1)
        self.ln(10)

    def footer(self):
        # Watermark: Sujal Vairagi
        self.set_y(-40)  # position higher from bottom
        self.set_font('Arial', 'B', 16)  # bold and larger font
        self.set_text_color(180, 180, 180)  # light gray
        self.cell(0, 10, 'Sujal Vairagi', 0, 0, 'C')

        # Page number
        self.set_y(-20)
        self.set_font('Arial', 'I', 10)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_section(self,title,content):
        self.set_font('Arial', 'B', 12)
        self.cell(0,10,title,ln=1)
        self.set_font('Arial', '', 11)

        if isinstance(content,dict):
            for key, value in content.items():
                self.multi_cell(0,8,f"{key} : {value}")

        elif isinstance(content,list):
            for item in content:
                self.cell(0,8,f"-{item}",ln=1)
        else:
            self.cell(0,8,content,ln=1)

        self.ln(5)
# generating the pdf
def generate_pdf_report(summary,output_path,data):
    pdf = PDFReport()
    pdf.add_page()

    pdf.add_section("Summary", {
        "Total Rows": summary["Total Rows"],
        "Columns": summary["Columns"]
    })
    pdf.add_section("Mean of Numeric Columns", summary["Mean of Numeric Columns"])

    pdf.add_section("Missing Values", summary["Missing Values"])

    #add correlation heatmap
    heatmap_path="correlation_heatmap.png"
    create_correlation_heatmap(data,heatmap_path)

    if os.path.exists(heatmap_path):
        pdf.image(heatmap_path,w=180)# resizing to fit the page

    pdf.output(output_path)
    return output_path
#step 5 main function
def main():
    file_path = input("Enter the file path to your CSV file: ").strip().strip('"')
    data = read_data(file_path)

    if data is not None:
        summary = analyze_data(data)

        # save pdf to desktop
        file_stem = Path(file_path).stem
        output_file = Path(f"{file_stem}_analysis_report.pdf")  # Save in current directory


        final_path = generate_pdf_report(summary, str(output_file),data)
        print(f"\n✅ PDF report saved to: {final_path}")
    else:
        print("Could not generate report because data is missing.")

 #run the programme

if __name__ == "__main__":
    main()
