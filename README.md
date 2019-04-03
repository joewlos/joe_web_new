# Joe Web (New)
#### APP STRUCTURE
```
- app.py
- models
    - property.py
    - shared.py
- templates
    - analytics.html
    - assessment.html
    - base.html
    - choropleth.html
    - habeas.html
    - index.html
    - page.html
    - presevent.html
    - uncommon.html
- static
    - css
        - stylesheet.css
    - data
        - info.json
    - documents
        - joe_wlos_resume.pdf
        - presevent.jpg
        - robots.txt
    - images
```
#### FLASK AND SQLALCHEMY
`app.py` initializes the Flask app and maps routes. It imports the database from `shared.py`. That same database is imported by `property.py`, where the model for the PostgreSQL database is declared. 

#### JSON FOR CONTENT
The website's content is declared on a JSON file in the data folder. This JSON file includes links to the individual HTML pages with text. For the income tax section, an iFrame loads the content, which is hosted externally.