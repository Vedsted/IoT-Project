create table Measurements
(
    id          bigint auto_increment
        primary key,
    group_id    varchar(255) not null,
    timestamp   mediumtext   not null,
    lux1        int          not null,
    lux2        int          not null,
    setpoint    int          not null,
    light_red   smallint     not null,
    light_green smallint     not null,
    light_blue  smallint     not null,
    constraint Measurements_Groups_id_fk
        foreign key (group_id) references `Groups` (id)
            on update cascade on delete cascade
);

