# Stream-of-Consciousness
Tool for musicians to track pay-per-stream (PPS) rates for various streaming platforms over time.


## Instructions
### Command line usage
Run with the following arguments:

- `filename`: path to the sales file exported from your distributor's back-office
- `distributor`: supported distributors
  - `cd_baby`
  - `distro_kid` (not yet supported)
- `transactions`: the transaction types to include in your earnings summary reports
  - `stream`
  - `download`
  - `royalty`
  - `youtube_audio_tier`
  
Example:
```
python distributor_report_analysis.py /path/to/export/file.txt cd_baby stream
```
