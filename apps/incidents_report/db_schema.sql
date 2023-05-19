CREATE TABLE dbo.freshservice_tickets (
	item_category VARCHAR (50),
	item_closed_at DATETIME,
	item_created_at DATETIME,
	item_id INT,
	item_first_responded_at DATETIME,
	item_category2 VARCHAR (50),
	item_reason_code_for_closing VARCHAR (50),
	item_requester_id bigINT,
	item_resolution_time_in_secs INT,
	item_resolved_at DATETIME,
	item_status VARCHAR (50),
	item_sub_category VARCHAR (50),
	item_type VARCHAR (50)
);

CREATE TABLE dbo.freshservice_requesters (
	requester_id bigINT,
	requester_company VARCHAR (255),
	location_id bigINT
);
CREATE TABLE dbo.freshservice_locations (
	location_id bigINT,
	location_name VARCHAR (255)
);

