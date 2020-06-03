# PhotoOrganizer

This is my project for organizing the over 19,000 photos I had terribly thrown about my various hard drives over many years.
I knew I had many duplicates in all my backups, and figured that the only way to organize photos long term was by date.
I built a script to recursively check a folder for files, note any duplicates, and organize them by year and date to an out directory. It's organized for a fairly specific function, but if you have tons and tons of photos you want to organize by modification/creation date, it might be useful.

Note that I used it to organize photos, but it will really work on any files at all. It only ever copies files, and if a file already exists it doesn't pave it, so it should be generally safe to use. You may accidentally end up with many files though.

Usage:
```
PhotoOrganizer.py -i <inputdirectory> -o <outputdirectory> -d -l
  -i: input directory. Program will recursively search this and all subfolders and 
        organize ALL found files
        
  -o: output directory. Program will organize all files found in a
        {outDir}/{Year}/{Month}/{file} structure. The file organization time is
        based on file modification or creation, whichever is *OLDER*
        
  -d: duplicate dump. This will add a "duplicates" folder at {outDir}/duplicates.
        If any duplicates are found, ALL same files will be dumped into this folder
        for visual comparison. Use if you think my duplication detection is done incorrectly.
        
  -l: log. This will dump a log txt file for reference at .py file location.
        This will contain all files found and any duplicates
```

Tested only on Windows, python 3.8. Use at your own risk.
