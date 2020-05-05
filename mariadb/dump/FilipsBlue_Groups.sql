create table `Groups`
(
    id            varchar(255) not null
        primary key,
    controller_id varchar(255) null,
    constraint Groups_Controllers_id_fk
        foreign key (id) references Controllers (id)
            on update cascade on delete cascade
);

