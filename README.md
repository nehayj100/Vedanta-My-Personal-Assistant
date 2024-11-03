# Personal AI Assistant

## Overview

The **Personal AI Assistant** is a local application designed to streamline your daily tasks. This intelligent assistant can write and send emails, read and analyze multiple PDF files, schedule meetings, search the internet, and ask clarifying questions when needed, all while ensuring your private information remains secure.

## Features

- **Email Management**: Automatically drafts and sends emails on your behalf, saving you time and effort.
- **PDF Analysis**: Reads multiple PDF files and provides answers to your questions based on the content.
- **Meeting Scheduling**: Efficiently schedules meetings according to your availability and preferences. It can either schdule the meeting at your desired time or can recommend you time as per your calendar on that day.
- **Internet Search**: Searches the web to find information you need quickly and accurately. It will give yopu top 10 search results with links and snippets and will also create a summary for you so you need not visit the links necessarily.
- **Interactive Querying**: Asks you clarifying questions when uncertain or when it requires personal information.

## Privacy Assurance

To ensure the security of your private information, the Personal AI Assistant runs entirely on a local model (Llama 3.2 1B). This setup eliminates the risk of data leakage that comes with cloud-based solutions.

## Methodology

### Local LLM Implementation

- **Model Used**: Llama 3.2 is utilized for all tasks, enabling efficient processing and ensuring privacy by keeping all data local.
- **Application Architecture**:
  - **Email Functionality**: Integrated SMTP protocols to handle email composition and sending.
  - **PDF Processing**: Implemented libraries for PDF reading and natural language processing to extract relevant information.
  - **Meeting Scheduling**: Integrated calendar APIs to facilitate seamless scheduling.
  - **Web Searching**: Utilized web scraping techniques to gather information from multiple sources.
  - **User Interaction**: Designed an interactive interface for querying and providing responses.

## Setup Instructions

1. **Requirements**:
   - Python 3.x
   - Necessary libraries (e.g., `requests`, `pdfplumber`, `smtplib`, etc.). Install all from requirements.txt
   
2. **Installation**:
   - Clone the repository:  
     ```bash
     git clone https://github.com/nehayj100/Vedanta-My-Personal-Assistant
     cd Vedanta-My-Personal-Assistant
     ```
   - Install required libraries:  
     ```bash
     pip install -r requirements.txt
     ```
3. **Get the following APIs**:
   - Create a folder confidential
   - Get credentials.json file from your google calendar API and paste it in the
     confidential folder.
   -  Get your google application password and paste it in confidential/email_pass.txt
   - Get your google custom search api and paste it in confidential/search_api.txt
   - Get your google custom search cx and paste it in confidential/search_cx.txt
   - Create a database of your contacts and paste it in confidential/email_pass.txt. The
     format should be like:
      NAME EMAIL
      abc: vedantjoshi370@gmail.com
      Neha Joshi: nehayj100@gmail.com
   - Add all the pdf files you need to answer your questions in paper folder.

4. **Run the Application**:
   - Start the assistant:  
     ```bash
     python pipeline.py
     ```

## Future Enhancements

- **Natural Language Understanding**: Improve the AI's ability to understand context and nuances in conversation.
- **Task Automation**: Extend capabilities to include more automated tasks, such as managing reminders and to-do lists.
- **Multi-language Support**: Implement support for additional languages to cater to a wider audience.

## Conclusion

The Personal AI Assistant is a versatile tool designed to enhance productivity while ensuring the security of your personal information. By leveraging local processing capabilities, it provides a reliable and private solution for managing your daily tasks effectively.
