-- Schema only, not a dump of demonstration or personal records.

-- Generated for the exercised SQLite dialect. Production PostgreSQL is not integration-tested.

CREATE TABLE provider_transactions (
	reference VARCHAR(80) NOT NULL,
	amount_tzs INTEGER NOT NULL,
	currency VARCHAR(3) NOT NULL,
	outcome VARCHAR(20) NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (reference)
);

CREATE TABLE roles (
	name VARCHAR(20) NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (name)
);

CREATE TABLE schools (
	name VARCHAR(150) NOT NULL,
	region VARCHAR(80) NOT NULL,
	active BOOLEAN NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE courses (
	school_id INTEGER NOT NULL,
	title VARCHAR(120) NOT NULL,
	subject VARCHAR(60) NOT NULL,
	form VARCHAR(20) NOT NULL,
	description TEXT NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(school_id) REFERENCES schools (id)
);

CREATE INDEX ix_courses_school_id ON courses (school_id);

CREATE TABLE subscription_plans (
	school_id INTEGER,
	name VARCHAR(80) NOT NULL,
	price_tzs INTEGER NOT NULL,
	days INTEGER NOT NULL,
	premium BOOLEAN NOT NULL,
	active BOOLEAN NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	CHECK (price_tzs > 0 AND days > 0),
	FOREIGN KEY(school_id) REFERENCES schools (id)
);

CREATE TABLE users (
	email VARCHAR(254) NOT NULL,
	name VARCHAR(100) NOT NULL,
	password_hash VARCHAR(300) NOT NULL,
	role_id INTEGER NOT NULL,
	school_id INTEGER NOT NULL,
	active BOOLEAN NOT NULL,
	language VARCHAR(2) NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(role_id) REFERENCES roles (id),
	FOREIGN KEY(school_id) REFERENCES schools (id)
);

CREATE INDEX ix_users_school_id ON users (school_id);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE TABLE assignments (
	course_id INTEGER NOT NULL,
	title VARCHAR(150) NOT NULL,
	instructions TEXT NOT NULL,
	due_at DATETIME,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(course_id) REFERENCES courses (id)
);

CREATE TABLE audit_logs (
	actor_id INTEGER NOT NULL,
	action VARCHAR(100) NOT NULL,
	entity VARCHAR(100) NOT NULL,
	detail VARCHAR(500) NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(actor_id) REFERENCES users (id)
);

CREATE INDEX ix_audit_logs_actor_id ON audit_logs (actor_id);

CREATE TABLE learning_materials (
	course_id INTEGER NOT NULL,
	title VARCHAR(150) NOT NULL,
	kind VARCHAR(20) NOT NULL,
	content TEXT NOT NULL,
	url VARCHAR(1000) NOT NULL,
	storage_key VARCHAR(100),
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(course_id) REFERENCES courses (id)
);

CREATE TABLE lessons (
	course_id INTEGER NOT NULL,
	title VARCHAR(150) NOT NULL,
	outline TEXT NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(course_id) REFERENCES courses (id)
);

CREATE TABLE notifications (
	user_id INTEGER NOT NULL,
	title VARCHAR(150) NOT NULL,
	body TEXT NOT NULL,
	read BOOLEAN NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_notifications_user_id ON notifications (user_id);

CREATE TABLE parents (
	user_id INTEGER NOT NULL,
	PRIMARY KEY (user_id),
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE quizzes (
	course_id INTEGER NOT NULL,
	title VARCHAR(150) NOT NULL,
	status VARCHAR(20) NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(course_id) REFERENCES courses (id)
);

CREATE TABLE students (
	user_id INTEGER NOT NULL,
	form VARCHAR(20) NOT NULL,
	interests VARCHAR(200) NOT NULL,
	preference VARCHAR(20) NOT NULL,
	PRIMARY KEY (user_id),
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE subscriptions (
	user_id INTEGER NOT NULL,
	plan_id INTEGER NOT NULL,
	status VARCHAR(30) NOT NULL,
	expires_at DATETIME,
	premium BOOLEAN NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES users (id),
	FOREIGN KEY(plan_id) REFERENCES subscription_plans (id)
);

CREATE INDEX ix_subscriptions_user_id ON subscriptions (user_id);

CREATE TABLE teachers (
	user_id INTEGER NOT NULL,
	specialization VARCHAR(100) NOT NULL,
	PRIMARY KEY (user_id),
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE tutor_messages (
	user_id INTEGER NOT NULL,
	subject VARCHAR(60) NOT NULL,
	language VARCHAR(2) NOT NULL,
	question TEXT NOT NULL,
	answer TEXT NOT NULL,
	source VARCHAR(200) NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE ai_recommendations (
	student_id INTEGER NOT NULL,
	course_id INTEGER NOT NULL,
	status VARCHAR(25) NOT NULL,
	content TEXT NOT NULL,
	reasons TEXT NOT NULL,
	version INTEGER NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(student_id) REFERENCES students (user_id),
	FOREIGN KEY(course_id) REFERENCES courses (id)
);

CREATE INDEX ix_ai_recommendations_student_id ON ai_recommendations (student_id);

CREATE TABLE assignment_policies (
	assignment_id INTEGER NOT NULL,
	max_attempts INTEGER NOT NULL,
	allow_resubmission BOOLEAN NOT NULL,
	allow_late BOOLEAN NOT NULL,
	require_feedback BOOLEAN NOT NULL,
	require_approval BOOLEAN NOT NULL,
	grading_policy VARCHAR(20) NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	CHECK (max_attempts BETWEEN 1 AND 20),
	CHECK (grading_policy IN ('first','best','latest','selected')),
	UNIQUE (assignment_id),
	FOREIGN KEY(assignment_id) REFERENCES assignments (id)
);

CREATE TABLE enrollments (
	student_id INTEGER NOT NULL,
	course_id INTEGER NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (student_id, course_id),
	FOREIGN KEY(student_id) REFERENCES students (user_id),
	FOREIGN KEY(course_id) REFERENCES courses (id)
);

CREATE TABLE learning_activities (
	student_id INTEGER NOT NULL,
	course_id INTEGER NOT NULL,
	action VARCHAR(60) NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(student_id) REFERENCES students (user_id),
	FOREIGN KEY(course_id) REFERENCES courses (id)
);

CREATE INDEX ix_learning_activities_student_id ON learning_activities (student_id);

CREATE TABLE messages (
	sender_id INTEGER NOT NULL,
	recipient_id INTEGER NOT NULL,
	student_id INTEGER NOT NULL,
	body TEXT NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(sender_id) REFERENCES users (id),
	FOREIGN KEY(recipient_id) REFERENCES users (id),
	FOREIGN KEY(student_id) REFERENCES students (user_id)
);

CREATE INDEX ix_messages_recipient_id ON messages (recipient_id);

CREATE TABLE parent_student_links (
	parent_id INTEGER NOT NULL,
	student_id INTEGER NOT NULL,
	status VARCHAR(20) NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (parent_id, student_id),
	FOREIGN KEY(parent_id) REFERENCES parents (user_id),
	FOREIGN KEY(student_id) REFERENCES students (user_id)
);

CREATE TABLE payments (
	subscription_id INTEGER NOT NULL,
	amount_tzs INTEGER NOT NULL,
	currency VARCHAR(3) NOT NULL,
	provider_reference VARCHAR(80) NOT NULL,
	status VARCHAR(30) NOT NULL,
	verified_at DATETIME,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (subscription_id),
	FOREIGN KEY(subscription_id) REFERENCES subscriptions (id),
	UNIQUE (provider_reference)
);

CREATE TABLE questions (
	quiz_id INTEGER NOT NULL,
	prompt TEXT NOT NULL,
	options TEXT NOT NULL,
	correct_index INTEGER NOT NULL,
	explanation TEXT NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(quiz_id) REFERENCES quizzes (id)
);

CREATE TABLE quiz_reviews (
	quiz_id INTEGER NOT NULL,
	teacher_id INTEGER NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(quiz_id) REFERENCES quizzes (id),
	FOREIGN KEY(teacher_id) REFERENCES teachers (user_id)
);

CREATE TABLE resubmission_approvals (
	assignment_id INTEGER NOT NULL,
	student_id INTEGER NOT NULL,
	attempt_number INTEGER NOT NULL,
	status VARCHAR(20) NOT NULL,
	reason TEXT NOT NULL,
	teacher_id INTEGER,
	comment TEXT NOT NULL,
	reopen_until DATETIME,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(assignment_id) REFERENCES assignments (id),
	FOREIGN KEY(student_id) REFERENCES students (user_id),
	FOREIGN KEY(teacher_id) REFERENCES teachers (user_id)
);

CREATE TABLE submissions (
	student_id INTEGER NOT NULL,
	assignment_id INTEGER,
	quiz_id INTEGER,
	content TEXT NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (student_id, assignment_id),
	UNIQUE (student_id, quiz_id),
	CONSTRAINT one_assessment CHECK ((assignment_id IS NULL) != (quiz_id IS NULL)),
	FOREIGN KEY(student_id) REFERENCES students (user_id),
	FOREIGN KEY(assignment_id) REFERENCES assignments (id),
	FOREIGN KEY(quiz_id) REFERENCES quizzes (id)
);

CREATE INDEX ix_submissions_student_id ON submissions (student_id);

CREATE TABLE teacher_course_assignments (
	teacher_id INTEGER NOT NULL,
	course_id INTEGER NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (teacher_id, course_id),
	FOREIGN KEY(teacher_id) REFERENCES teachers (user_id),
	FOREIGN KEY(course_id) REFERENCES courses (id)
);

CREATE TABLE grades (
	submission_id INTEGER NOT NULL,
	score FLOAT NOT NULL,
	feedback TEXT NOT NULL,
	grader_id INTEGER,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	CHECK (score >= 0 AND score <= 100),
	UNIQUE (submission_id),
	FOREIGN KEY(submission_id) REFERENCES submissions (id),
	FOREIGN KEY(grader_id) REFERENCES users (id)
);

CREATE TABLE question_settings (
	question_id INTEGER NOT NULL,
	kind VARCHAR(20) NOT NULL,
	answer TEXT NOT NULL,
	language VARCHAR(2) NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (question_id),
	FOREIGN KEY(question_id) REFERENCES questions (id)
);

CREATE TABLE quiz_responses (
	submission_id INTEGER NOT NULL,
	parts TEXT NOT NULL,
	manual_marks TEXT NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (submission_id),
	FOREIGN KEY(submission_id) REFERENCES submissions (id)
);

CREATE TABLE recommendation_approvals (
	recommendation_id INTEGER NOT NULL,
	teacher_id INTEGER NOT NULL,
	decision VARCHAR(20) NOT NULL,
	comment TEXT NOT NULL,
	version INTEGER NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(recommendation_id) REFERENCES ai_recommendations (id),
	FOREIGN KEY(teacher_id) REFERENCES teachers (user_id)
);

CREATE TABLE recommendation_revisions (
	recommendation_id INTEGER NOT NULL,
	version INTEGER NOT NULL,
	content TEXT NOT NULL,
	reasons TEXT NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (recommendation_id, version),
	FOREIGN KEY(recommendation_id) REFERENCES ai_recommendations (id)
);

CREATE TABLE submission_attempts (
	submission_id INTEGER NOT NULL,
	number INTEGER NOT NULL,
	content TEXT NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (submission_id, number),
	CHECK (number > 0),
	FOREIGN KEY(submission_id) REFERENCES submissions (id)
);

CREATE INDEX ix_submission_attempts_submission_id ON submission_attempts (submission_id);

CREATE TABLE attempt_grades (
	attempt_id INTEGER NOT NULL,
	score FLOAT NOT NULL,
	feedback TEXT NOT NULL,
	grader_id INTEGER NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	CHECK (score >= 0 AND score <= 100),
	UNIQUE (attempt_id),
	FOREIGN KEY(attempt_id) REFERENCES submission_attempts (id),
	FOREIGN KEY(grader_id) REFERENCES teachers (user_id)
);

CREATE TABLE final_grade_selections (
	submission_id INTEGER NOT NULL,
	attempt_id INTEGER NOT NULL,
	teacher_id INTEGER NOT NULL,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (submission_id),
	FOREIGN KEY(submission_id) REFERENCES submissions (id),
	FOREIGN KEY(attempt_id) REFERENCES submission_attempts (id),
	FOREIGN KEY(teacher_id) REFERENCES teachers (user_id)
);

CREATE TABLE grade_history (
	attempt_id INTEGER NOT NULL,
	score FLOAT NOT NULL,
	feedback TEXT NOT NULL,
	grader_id INTEGER,
	id INTEGER NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(attempt_id) REFERENCES submission_attempts (id),
	FOREIGN KEY(grader_id) REFERENCES users (id)
);
