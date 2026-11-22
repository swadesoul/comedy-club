-- Previously approved original characters: actual editorial records, no fabricated shows.
-- status in_development makes audio-production readiness explicit.
INSERT INTO maestroradio.comedy_comedians
(slug,display_name,biography,artwork_path,default_rating,status,rights_confirmed)
VALUES
('marcus','Marcus “Big Truth” Coleman','Original observational comedy about family, everyday life and technology.','/comedy-club/assets/comedians/marcus.svg','PG-13','in_development',true),
('tasha','Tasha “No Filter” Monroe','Original character performing relationship and family stories with quick crowd conversations.','/comedy-club/assets/comedians/tasha.svg','PG-13','in_development',true),
('eddie','Eddie “Sideways” Miller','Original character exploring dry absurdism, unlikely everyday situations and understated timing.','/comedy-club/assets/comedians/eddie.svg','PG','in_development',true),
('jamal','Jamal “Quickfire” Banks','Original character specializing in fast comebacks and interactive crowd work.','/comedy-club/assets/comedians/jamal.svg','PG-13','in_development',true),
('pearl','Auntie Pearl','Original character sharing generational wisdom and family stories.','/comedy-club/assets/comedians/pearl.svg','PG','in_development',true),
('reggie','Uncle Reggie Brooks','Original character focused on clean family storytelling and generational humor.','/comedy-club/assets/comedians/reggie.svg','PG','in_development',true)
ON CONFLICT(slug) DO NOTHING;
