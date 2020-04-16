// Sample schema for Apache Cassandra

// IF EXISTS added for Cassandra 2.1
// CQL 3.1.0
DROP KEYSPACE IF EXISTS elt;
CREATE KEYSPACE elt WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

use elt;

// User Defined Type introduced in CQL 3.2 spec
CREATE TYPE obs_schema (
   obs_id bigint,
   voided boolean,
   concept_id bigint,
   obs_datetime timestamp,
   value text,
   value_type varchar,
   obs_group_id bigint,
   parent_concept_id bigint

);

// User Defined Type introduced in CQL 3.2 spec
CREATE TYPE orders_schema (
   order_id bigint,
   voided boolean,
   order_concept_id bigint,
   date_activated timestamp

);

// Entity table 
CREATE TABLE flat_obs_orders (
   patient_id bigint,
   encounter_id bigint,
   location_id bigint,
   visit_id bigint,
   encounter_datetime timestamp,
   encounter_type int,
   dead boolean,
   gender varchar,
   death_date timestamp,
   patient_uuid uuid,
   visit_type_id int,
   birthdate timestamp,
   obs List  <frozen<obs_schema>>,
   orders List  <frozen<orders_schema>>,
   PRIMARY KEY (patient_id,encounter_id,encounter_datetime)
) WITH CLUSTERING ORDER BY (encounter_id DESC, encounter_datetime DESC);

