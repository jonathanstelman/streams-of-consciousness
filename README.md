# Streams of Consciousness
A Streamlit app that enables musicians to review pay-per-stream (PPS) rates for various streaming platforms over time.

## Mission Statement
Streams of Consciousness is born from an idea that musicians should have more choice in how audiences pay for their products. While major streaming platforms have seen increased revenue over the last several years, musicians still earn less in take-home pay year over year. We believe that clear information about the payout rates offered by different services will enable musicians to direct their audiences to preferred streaming platforms, and provide music listeners with the ability to select the platform that best compensates the musicians they love.

## What Is It?
Streams of Consciousness is a collection of tools for musicians, available as both a web app and as a Google Sheet. The tools calculate the payment the musician earned from each streaming service, and compare the PPS (pay per stream) rate from each. The tools are available for musicians who distribute with CDBaby or DistroKid. We plan to add support for more distributors in the future.

### Why multiple tools?
We’ve thought a lot about how to guarantee the privacy of users’ data. Financial data is very sensitive, and we never want your data to be outside of your control. (We really don’t want to assume the risk of storing your sensitive data either!) We’ve chosen to release the web app as free and open source software (FOSS), which ensures that the full source code can be reviewed by anyone, to verify that it is safe. The source code can be downloaded by users and run locally, so your data never leaves your computer.  
  
But not everyone should be expected to review computer code before running it. Google Sheets provides an alternative for users who are more comfortable uploading data to their Google account. All of the logic lives in Google Sheets, so you can be sure that your financial data is kept secure by Google.  
  
Whether you choose the web app, run the program locally, or use the Google Sheets template, you can be sure that your financial data is never accessible to us.  

## Why It Matters
In theory, independent musicians have the freedom to choose where to make their music available for streaming and purchase. However, lack of transparency by streaming companies and frequently changing PPS rates make it difficult for musicians to follow and adjust their marketing strategy. By making this information easily accessible, we hope to help musicians make more informed decisions about the stores they choose to promote their music in.  
  
Additionally, we hope that more up-to-date information regarding streaming rates will help direct music fans towards platforms who do a better job paying musicians for their work.  

## Who Is It For
The tools are meant for individual musicians and labels who use CDBaby or DistroKid as their distributor.

## How This Can Be Used
- Better understand your sales and streams data
- See how your music sales have changed over time
- See which streaming platforms paid more or less
- Direct your followers towards your preferred platforms
- Advise your followers which platforms they should use, and which they should avoid
- Spark conversations about fair-trade music. 
- Ensure your audience can understand how their listening choices impact your livelihood

## How To Get Involved
### As a developer
Review our GitHub repository and our project roadmap. We are actively seeking help from contributors who can review and test our code for efficiency, security, and work on other enhancements.

### As a beta tester
We are looking for musicians who would like to be among the first to try the Streams of Consciousness tools. If you manage your distribution through CDBaby or DistroKid and can spend an hour or two learning to use the tools to give feedback, [please use this form to get in touch!](https://forms.gle/DUCwfQdfzV9fD7Q8A)


## Installation and Usage
### Install with `poetry`
`poetry install`
`poetry shell`

### Launch Streamlit web app
`streamlit run src/streamlit_app.py`

### Command line usage
Run with the following arguments:

- `filename`: path to the sales file exported from your distributor's back-office
- `distributor`: supported distributors
  - `cd_baby`
  - `distrokid` (not yet supported)
- `transactions`: the transaction types to include in your earnings summary reports
  - `stream`
  - `download`
  - `royalty`
  - `youtube_audio_tier`
  
Example:
```
python src/main.py /path/to/export/file.txt cd_baby stream
```
