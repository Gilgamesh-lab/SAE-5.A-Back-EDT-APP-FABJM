SET SEARCH_PATH TO EDT;

-- Utilisateur (IdUtilisateur, FirstName, LastName, Username, PassWord, FirstLogin)
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Junko', 'Enoshima', 'monokuma', 'despair');
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Gilgamesh', 'Elish', 'Uruk', 'Enkidu');
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Aya', 'Rindo', 'detective', 'immortal');
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Tsugaru ', 'Shinuchi', 'assistant', 'OniKiller');


INSERT INTO Semestre (Numero) values (3);
INSERT INTO Ressource (Titre, Numero, NbrHeureSemestre, idSemestre) values ('test ', 'R3-04', '10', '1');


-- Cours (idCours, HeureDebut, NombreHeure, Jour, idRessource)

INSERT INTO Cours (HeureDebut, NombreHeure, Jour, idRessource) values ('20:18:06 ', '2', '2023-12-06', '1');
INSERT INTO Cours (HeureDebut, NombreHeure, Jour, idRessource) values ('16:49:49 ', '2', '2023-10-06', '1');


-- Salle (idSalle, Numero ,Capacite);
INSERT INTO Salle (Numero, Capacite) values ('A2-05', 35);
INSERT INTO Salle (Numero, Capacite) values ('A1-01', 20);

-- Professeur(idProf, Initiale, idSalle, idUtilisateur);
INSERT INTO Professeur( Initiale, idSalle, idUtilisateur) values ('AR', 1, 3);