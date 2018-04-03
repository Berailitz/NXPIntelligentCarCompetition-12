## IP Monitor

#### API
- [x] GET /api/group?id={group_id}
- [ ] PUT /api/group?id={group_name}
- [ ] DELETE /api/group?id={group_id}
- [x] GET /api/host?id={host_id}
- [ ] PUT /api/host?id={host_name}&group_id={group_id}
- [ ] DELETE /api/host?id={host_id}
- [x] GET /api/ip?id={ip_id}
- [x] POST /api/ip?id={ip_id}&ip={ip, option}
- [ ] PUT /api/ip?host_id={host_id}&ip_type={ip_type, option}&ip={ip, option}
- [ ] DELETE /api/ip?id={ip_id}

#### Components
- Card: MD card, with a title (group name or host name), a table (host id, host name, IPs, etc) and a refresh button
- IP: One IPv4 address or IPv6 address, marked by id
- Host: Each host has at least one IP attached to it, marked by id and name
- Group: Each group has at least one host in it, marked by id and name

#### Page URLs
- [x] /host/{host_id}: List IPs attached to a specific host, one card
- [x] /group/{group_id}: List IPs attached to specific hosts in a group, one card
- [ ] /admin: Add and delete IPs, hosts and groups.

#### Templates
- [x] /host/{host_id}: Table rendered by JavaScript, card rendered by server, one card per page
- [x] /group/{host_id}: Table rendered by JavaScript, card rendered by server, one card per page
- [ ] /admin: Layout rendered by server

#### Database
- [x] IP: One IP per item, including `host`(foreign key by relation), `host_id`(int), `id`(int, primary key), `ip`(str, 39), `ip_type`(int) and `update_time`(Datetime)
- [x] Host: One host per item, including `group`(foreign key by relation), `group_id`(foreign key), `id`(int, primary key), `ips`(foreign key by relation), and `name`(str, 40)
- [x] Group: One group per item, including `id`(int), `hosts`(foreign key by relation) and `name`(str, 40)

#### SQL Handler
- [x] Update IP: Check IP and save it, return IP object or None.
- [x] Get *: Return a object with a specific id.
- [ ] Add *: Insert row, return object.
- [ ] Delete *: Delete row from id, return True for success.
