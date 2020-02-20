CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `debezium`@`%` 
    SQL SECURITY DEFINER
VIEW `obs_view` AS
    SELECT 
        `obs`.`obs_id` AS `obs_id`,
        `obs`.`person_id` AS `person_id`,
        `obs`.`concept_id` AS `concept_id`,
        `obs`.`encounter_id` AS `encounter_id`,
        `obs`.`order_id` AS `order_id`,
        `obs`.`obs_datetime` AS `obs_datetime`,
        `obs`.`location_id` AS `location_id`,
        `obs`.`obs_group_id` AS `obs_group_id`,
        `obs`.`accession_number` AS `accession_number`,
        `obs`.`value_group_id` AS `value_group_id`,
        `obs`.`value_coded` AS `value_coded`,
        `obs`.`value_coded_name_id` AS `value_coded_name_id`,
        `obs`.`value_drug` AS `value_drug`,
        `obs`.`value_datetime` AS `value_datetime`,
        `obs`.`value_numeric` AS `value_numeric`,
        `obs`.`value_modifier` AS `value_modifier`,
        `obs`.`value_text` AS `value_text`,
        `obs`.`comments` AS `comments`,
        `obs`.`creator` AS `creator`,
        `obs`.`date_created` AS `date_created`,
        `obs`.`voided` AS `voided`,
        `obs`.`voided_by` AS `voided_by`,
        `obs`.`date_voided` AS `date_voided`,
        `obs`.`void_reason` AS `void_reason`,
        `obs`.`value_complex` AS `value_complex`,
        `obs`.`uuid` AS `uuid`,
        `obs`.`previous_version` AS `previous_version`,
        `obs`.`form_namespace_and_path` AS `form_namespace_and_path`,
        `obs`.`status` AS `status`,
        `obs`.`interpretation` AS `interpretation`
    FROM
        `obs`
    WHERE
        ((`obs`.`encounter_id` IS NOT NULL)
            AND ((`obs`.`voided` = 0)
            OR ISNULL(`obs`.`voided`)))