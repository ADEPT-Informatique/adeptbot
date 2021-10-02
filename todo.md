# Todo

## Users controler

1. GET /users/{pageIndex}
2. GET /users/short/{pageIndex}
3. POST /users
4. GET /users/{userId}
5. PUT /users/{userId}
6. DELETE /users/{userId}
7. POST /users/{userId}/activate
8. POST /users/{userId}/deactivate

## Roles/Permissions controller

1. GET /roles
2. POST /roles
3. PUT /roles/{roleId}
4. DELETE /roles/{roleId}
5. GET /permissions
6. POST /permissions
7. PUT /permissions/{roleId}
8. DELETE /permissions/{roleId}

## Discord

1. GET /discord/mute
2. POST /discord/mute
3. DELETE /discord/mute/{userId}?reason=
4. GET /discord/ban
5. POST /discord/ban
6. DELETE /discord/ban/{userId}?reason=
7. GET /discord/user/{userId}
8. POST /discord/user
9. PUT /discord/user/{userId}

## Membre de confiance

1. GET /membreconfiance/applications
1. POST /membreconfiance/applications
1. POST /membreconfiance/applications/accept
1. POST /membreconfiance/applications/refuse

## Auth Controller

1. login
2. register
3. auth0 login/register

## Generics

1. GET CA

## Hoodies controller

1. GET /hoodies
2. GET /hoodies/logs
3. POST /hoodies/reservation
4. GET /hoodies/reservation/{reservationId}
5. PUT /hoodies/rservation/{reservationId}
6. PUT /hoodie/transation/{reservationId}
7. DELETE /hooides/reservation/{reservationId}

# LAN

## Seat controller

1. POST /seat/book/{seat_id}
2. DELETE /seat/book/{seat_id}

### admin

3. POST /seat/confirm/{seat_id}
4. DELETE /seat/confirm/{seat_id}
5. POST /seat/assign/{seat_id}
6. DELETE /seat/assign/{seat_id}
7. GET /seat/charts

## Team controller

1. POST /team
2. POST /team/request
3. GET /team/request
4. GET /team/user
5. GET /team/details
6. PUT /team/leader
7. POST /team/accept
8. POST /team/leave
9. DELETE /team/kick
10. DELETE /team/leader
11. DELETE /team/request/leader
12. DELETE /team/request/player

## LAN controller

### admin

1. POST /lan
2. POST /lan/current
3. PUT /lan
4. POST /lan/image
5. DELETE /lan/image

## Tournament controller

### admin

1. POST tournament
2. PUT tournament/{tournament_id}
3. DELETE tournament/{tournament_id}
4. POST tournament/{tournament_id}/quit
5. GET tournament/all/organizer
6. POST tournament/{tournament_id}/organizer
7. DELETE tournament/{tournament_id}/organizer
8. DELETE team/admin
