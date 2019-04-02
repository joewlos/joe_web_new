# -*- coding: utf-8 -*-
'''
PROPERTY MODEL
'''
from shared import db
from sqlalchemy import and_, between
from sqlalchemy.orm import aliased

# Property model from scraped data
class Properties(db.Model):
	__tablename__ = "properties"

	# Primary Key
	id = db.Column("pin14_id", db.BIGINT, primary_key=True)

	# Data
	age = db.Column(db.Integer)
	air = db.Column(db.TEXT)
	apartments = db.Column(db.Integer)
	assessor_office_url = db.Column(db.TEXT)
	attic = db.Column(db.TEXT)
	basement = db.Column(db.TEXT)
	building_assessed_2015 = db.Column(db.Integer)
	building_assessed_2016 = db.Column(db.Integer)
	building_sqft = db.Column(db.Integer)
	city = db.Column(db.TEXT)
	classification = db.Column(db.Integer)
	desc = db.Column(db.TEXT)
	est_market_value_2015 = db.Column(db.Integer)
	est_market_value_2016 = db.Column(db.Integer)
	exterior = db.Column(db.TEXT)
	fireplaces = db.Column(db.Integer)
	full_baths = db.Column(db.Integer)
	half_baths = db.Column(db.Integer)
	garage = db.Column(db.TEXT)
	image_url = db.Column(db.TEXT)
	land_assessed_2015 = db.Column(db.Integer)
	land_assessed_2016 = db.Column(db.Integer)
	land_sqft = db.Column(db.Integer)
	neighborhood = db.Column(db.Integer)
	official_pin14 = db.Column(db.TEXT)
	property_location = db.Column(db.TEXT)
	res_type = db.Column(db.TEXT)
	township = db.Column(db.TEXT)
	use = db.Column(db.TEXT)

	# Init
	def __init__(
		self,
		id, 
		age, 
		air, 
		apartments, 
		assessor_office_url, 
		attic, 
		basement,
		building_assessed_2015, 
		building_assessed_2016, 
		building_sqft, 
		city, 
		classification,
		desc, 
		est_market_value_2015,
		est_market_value_2016,
		exterior,
		fireplaces, 
		full_baths, 
		half_baths, 
		garage, 
		image_url,
		land_assessed_2015, 
		land_assessed_2016, 
		land_sqft, 
		neighborhood, 
		official_pin14, 
		property_location,
		res_type, 
		township, 
		use
	):
		self.pin14_id = id
		self.age = age
		self.air = air
		self.apartments = apartments
		self.assessor_office_url = assessor_office_url
		self.attic = attic
		self.basement = basement
		self.building_assessed_2015 = building_assessed_2015
		self.building_assessed_2016 = building_assessed_2016
		self.building_sqft = building_sqft
		self.city = city
		self.classification = classification
		self.desc = desc
		self.est_market_value_2015 = est_market_value_2015
		self.est_market_value_2016 = est_market_value_2016
		self.exterior = exterior
		self.fireplaces = fireplaces
		self.full_baths = full_baths
		self.half_baths = half_baths
		self.garage = garage
		self.image_url = image_url
		self.land_assessed_2015 = land_assessed_2015
		self.land_assessed_2016 = land_assessed_2016
		self.land_sqft = land_sqft
		self.neighborhood = neighborhood
		self.official_pin14 = official_pin14
		self.property_location = property_location
		self.res_type = res_type
		self.township = township
		self.use = use

	# Representation
	def __repr__(self):
		return '<pin14 %r>' % self.id

	# Query the properties overvalued by $100 or more
	@classmethod
	def get_overvalued(class_):
		Properties = class_
		
		# Alias for the matching properties
		s = aliased(Properties, name='matching_properties')

		# Join the table to the subquery
		q = Properties.query.join(
			s, and_(
				Properties.id != s.id,
				Properties.neighborhood == s.neighborhood,
				Properties.air == s.air,
				Properties.attic == s.attic,
				Properties.basement == s.basement,
				Properties.garage == s.garage,
				Properties.exterior == s.exterior,
				Properties.classification == s.classification,
				Properties.fireplaces <= s.fireplaces,
				Properties.full_baths <= s.full_baths,
				Properties.half_baths <= s.half_baths,
				Properties.apartments <= s.apartments,
				between(Properties.building_sqft, s.building_sqft - 50, s.building_sqft + 50),
				between(Properties.building_sqft, s.land_sqft - 50, s.land_sqft + 50),
				Properties.est_market_value_2016 >= s.est_market_value_2016 + 100
			)
		).add_columns(
			Properties.id,
			Properties.property_location,
			Properties.city,
			Properties.est_market_value_2016,
			s.id.label('match_id'),
			s.est_market_value_2016.label('match_est_market_value_2016'),
			s.property_location.label('match_property_location'),
			s.city.label('match_city')
		).all()

		# Convert the results to a list of dicts
		query = [x._asdict() for x in q]
		results = {}
		for row in query:

			# Add a result if it is not present
			if row['id'] not in results.keys():
				results[row['id']] = {
					'value_2016': row['est_market_value_2016'],
					'city': row['city'],
					'property_location': row['property_location'],
					'matches': [{
						'match_id': row['match_id'],
						'value_2016': row['match_est_market_value_2016'],
						'match_city': row['match_city'],
						'match_property_location': row['match_property_location']
					}]
				}

			# Append a match to the result if it is
			else:
				results[row['id']]['matches'].append({
					'match_id': row['match_id'],
					'value_2016': row['match_est_market_value_2016'],
					'match_city': row['match_city'],
					'match_property_location': row['match_property_location']
				})

			# Calculate the stats
			matches = results[row['id']]['matches']
			results[row['id']]['count_match'] = len(matches)
			results[row['id']]['avg_match'] = sum([x['value_2016'] for x in matches]) / len(matches)

		# Return the results
		return results