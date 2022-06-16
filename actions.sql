CREATE TABLE "actions" (
	"action" TEXT NOT NULL,
	pluginmap TEXT NOT NULL,
	category TEXT,
	description TEXT,
	"position" INTEGER,
	CONSTRAINT actions_UN UNIQUE ("action")
);