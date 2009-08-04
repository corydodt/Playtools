
start:
	hg serve --daemon --port 28084 --pid-file hgserve.pid

stop:
	kill `cat hgserve.pid`

n3:
	cd playtools/data; \
		cp -av spell.n3 armor.n3 /var/www/goonmill.org/2009; \
		cp -av characteristic.n3 dice.n3 family.n3 feat.n3 monster.n3 \
			pcclass.n3 player.n3 property.n3 skill.n3 \
			sparqly.n3 specialAbility.n3 /var/www/goonmill.org/2007
