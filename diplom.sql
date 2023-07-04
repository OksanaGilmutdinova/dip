create table if not exists viewed (
profile_id int
, user_id int
, constraint pk_vw primary key (profile_id, user_id)
);


