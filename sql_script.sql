SELECT 
	s.session_id,
	s.user_id,
	CAST(session_start::DATE = u.regisrtation AS INT) AS is_new_user,
	u.country,
	s.session_start,
	s.session_end,
	s.platform,
	s.game_id,
	s.session_status
FROM sessions s
JOIN users u ON s.user_id = u.user_id
JOIN games g ON s.game_id = g.game_id
ORDER BY s.session_id;
