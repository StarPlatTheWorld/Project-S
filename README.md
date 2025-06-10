# Project S

## What's Project S?
Project S is an online dependency scanner that allows users to upload dependency files (requirements.txt) and receive scan results based on a custom vulnerability database.

## How does it work?
The user clicks on the file upload button, selects their dependency file, and submits it to the API. The file content is then compared to a custom MongoDB database and results are returned based on matched content.

## Future Updates
Currently the database is small and doesn't hold much content, which could be improved upon and mainstreamed by pulling from an external API or manual insertion of data. 

The front-end is basic and doesn't include much styling and the file submit function could be more optimized.
