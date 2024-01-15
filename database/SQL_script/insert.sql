SET SEARCH_PATH TO EDT;

-- Utilisateur (IdUtilisateur, FirstName, LastName, Username, PassWord, FirstLogin)
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Junko', 'Enoshima', 'monokuma', 'despair'); -- élève
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Gilgamesh', 'Elish', 'Uruk', 'Enkidu'); -- admin
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Aya', 'Rindo', 'detective', 'immortal'); -- professeur
INSERT INTO Utilisateur (FirstName, LastName, Username, PassWord) values ('Tsugaru ', 'Shinuchi', 'assistant', 'OniKiller');


-- Admin (idAdmin, idUtilisateur)
INSERT INTO Admin (idUtilisateur) values (2);
-- Semestre(idSemestre, Numero)
INSERT INTO Semestre (Numero) values (3);

-- Ressource(idRessource, Titre, Numero, NbrHeureSemestre, CodeCouleur, idSemestre)
INSERT INTO Ressource (Titre, Numero, NbrHeureSemestre, idSemestre) values ('Dev', 'R3-04', '10:00:00', '1');
INSERT INTO Ressource (Titre, Numero, NbrHeureSemestre, idSemestre) values ('Math', 'R3-12', '08:00:00', '1');


-- Cours (idCours, HeureDebut, NombreHeure, Jour, idRessource)

INSERT INTO Cours (HeureDebut, NombreHeure, Jour, idRessource) values ('20:18:06 ', '02:00:00', '2023-12-06', '1');
INSERT INTO Cours (HeureDebut, NombreHeure, Jour, idRessource) values ('16:49:49 ', '02:00:00', '2023-10-06', '1');
INSERT INTO Cours (HeureDebut, NombreHeure, Jour, idRessource)
VALUES 
  ('10:00:00', '02:30:00', '2024-01-05', '1'),
  ('14:30:00', '03:00:00', '2024-01-10', '1'),
  ('09:15:00', '02:30:00', '2024-01-15', '1'),
  ('13:45:00', '02:00:00', '2024-01-20', '1'),
  ('11:30:00', '03:00:00', '2024-01-25', '1'),
  ('15:00:00', '02:30:00', '2024-01-30', '1');



-- Salle (idSalle, Numero ,Capacite);
INSERT INTO Salle (Numero, Capacite) values ('A2-05', 35);
INSERT INTO Salle (Numero, Capacite) values ('A1-01', 20);

-- Groupe(idGroupe ,Nom, AnneeScolaire,Annee ,idGroupe_parent)
INSERT INTO Groupe(Nom, AnneeScolaire,Annee ) values ('A1', 1, 2023);

-- Professeur(idProf, Initiale, idSalle, idUtilisateur)
INSERT INTO Professeur(Initiale, idSalle, idUtilisateur) values ('AR', 1, 3);

-- Enseigner(idProf, idCours)
INSERT INTO Enseigner(idProf, idCours) values (1,1);
INSERT INTO Enseigner(idProf, idCours) 
values 
(1,2),
(1,3),
(1,4),
(1,5),
(1,6),
(1,7),
(1,8);

-- Etudier(idgroupe, idcours)
INSERT INTO Etudier(idgroupe, idcours) values (1,1);

-- Eleve(idEleve,idGroupe,idUtilisateur)
INSERT INTO Eleve(idGroupe,idUtilisateur) values (1,1);

-- Responsable(idProf, idRessource)
INSERT INTO Responsable(idProf, idRessource) values (1,1);

-- Accuellir(idSalle, idCours)
INSERT INTO Accuellir(idSalle, idCours) values (2,1);
