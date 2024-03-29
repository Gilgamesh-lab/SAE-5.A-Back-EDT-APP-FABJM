from flask import Blueprint, request, jsonify
from flask_cors import CORS

import src.connect_pg as connect_pg
import src.apiException as apiException

from src.config import config
from src.services.salle_service import get_salle_statement
from src.services.equipement_service import get_equipement_statement

import src.services.permision as perm
import src.services.verification as verif 

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import OperationalError, Error

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity  
import datetime
salle = Blueprint('salle', __name__)

# TODO: Update salle

@salle.route('/salle/getDispo', methods=['GET', 'POST'])
def get_salle_dispo():
    """Renvoit toutes les salles disponible sur une période via la route /salle/getDispo

    :param HeureDebut: date du début de la période au format time(hh:mm:ss) spécifié dans le body
    :type HeureDebut: str 

    :param NombreHeure: durée de la période au format TIME(hh:mm:ss) spécifié dans le body
    :type NombreHeure: int

    :param Jour: date de la journée où la disponibilité des salles doit être vérifer au format DATE(yyyy-mm-dd)
    :type Jour: str

    :raises AucuneDonneeTrouverException: Si aucune donnée n'a été trouvé dans la table groupe, etudier ou cours
    :raises ParamètreBodyManquantException: Si un paramètre est manquant
    :raises ParamètreInvalideException: Si un des paramètres est invalide
    :raises ActionImpossibleException: Si une erreur est survenue lors de la récupération des données
    
    :return: toutes les salles disponibles
    :rtype: flask.wrappers.Response(json)
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error ': 'missing json body'}), 400
    
    heureDebut_str = json_data['HeureDebut']  
    nombreHeure_str = json_data['NombreHeure'] 
    jour_str = json_data['Jour']
    
    if not heureDebut_str or not nombreHeure_str or not jour_str:
        return jsonify({'error ': 'missing json body'}), 400
    
    salles = []
    heureDebut = datetime.datetime.strptime(heureDebut_str, '%H:%M:%S').time()
    nombreHeure = datetime.datetime.strptime(nombreHeure_str, '%H:%M:%S').time()
    jour = datetime.datetime.strptime(jour_str, '%Y-%m-%d').date()
    
    debut = datetime.datetime.combine(jour, heureDebut)
    fin = datetime.datetime.combine(jour, heureDebut) + datetime.timedelta(hours=nombreHeure.hour, minutes=nombreHeure.minute, seconds=nombreHeure.second)
       
    conn = connect_pg.connect()
    query = f"select * from edt.salle;"
    try:
        salles = connect_pg.get_query(conn, query)
    except:
        return jsonify({'error': str(apiException.ActionImpossibleException("salle", "récuperer"))}), 500
    
    rows = []
    query = f"select * from edt.accuellir inner join edt.cours using(idcours) where edt.cours.jour = '{jour}';"
    try:
        rows = connect_pg.get_query(conn, query)
    except:
        return jsonify({'error': str(apiException.ActionImpossibleException("accuellir", "récuperer"))}), 500
        
    returnStatement = []
    for salle in salles:
        is_dispo = True
        for row in rows:
            rowHeureDebut = row[2]
            nombreHeure = row[3]
            rowJour = row[4]
            rowDebut = datetime.datetime.combine(rowJour, rowHeureDebut)
            rowFin = datetime.datetime.combine(rowJour, rowHeureDebut) + datetime.timedelta(hours=nombreHeure.hour, minutes=nombreHeure.minute, seconds=nombreHeure.second)
            if salle[0] == row[1]:
                #if debut is between rowDebut and rowFin or if fin is between rowDebut and rowFin
                if ((debut > rowDebut and debut < rowFin) or (fin > rowDebut and fin < rowFin)):
                    is_dispo = False
                    
                elif ((rowDebut > debut and rowDebut < fin) or (rowFin > debut and rowFin < fin)):
                    is_dispo = False

        if is_dispo:
            returnStatement.append(get_salle_statement(salle))
    connect_pg.disconnect(conn)
    return jsonify(returnStatement), 200
    

@salle.route('/salle/getAll', methods=['GET'])
@jwt_required()
def get_salle():
    """Renvoit toutes les salles via la route /salle/getAll

    :raises AucuneDonneeTrouverException: Si aucune donnée n'a été trouvé dans la table salle
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la récupération des données
    
    :return: toutes les salles
    :rtype: json
    """
    query = "SELECT * from edt.salle order by idsalle asc"
    conn = connect_pg.connect()
    
    returnStatement = []
    try:
        rows = connect_pg.get_query(conn, query)
        if rows == []:
            return jsonify({'error': str(apiException.AucuneDonneeTrouverException("salle"))}), 404
        for row in rows:
            returnStatement.append(get_salle_statement(row))
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("salle", "récuperer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)

@salle.route('/salle/get/<idSalle>', methods=['GET', 'POST'])
@jwt_required()
def get_one_salle(idSalle):
    """Renvoit une salle spécifié par son id via la route /salle/get<idSalle>

    :param idSalle: id d'une salle présent dans la base de donnée
    :type idSalle: int

    :raises DonneeIntrouvableException: Impossible de trouver la salle spécifié dans la table salle
    :raises ParamètreTypeInvalideException: Le type de l'id salle est invalide, une valeur de type int est attendue
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la récupération des données

    :return: la salle qui correspond à l'id du numéro entré en paramètre
    :rtype: json
    """
    if (not idSalle.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idSalle", "int"))}), 400
    
    query = f"SELECT * from edt.salle where idSalle='{idSalle}'"

    conn = connect_pg.connect()
    
    returnStatement = {}
    if not idSalle.isdigit() or type(idSalle) is not str:
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idSalle", "numérique"))}), 400
    try:
        rows = connect_pg.get_query(conn, query)
        if len(rows) == 0:
            return jsonify({'error': str(apiException.DonneeIntrouvableException("salle", idSalle))}), 404
        returnStatement = get_salle_statement(rows[0])
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("salle", "récuperer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement), 200

@salle.route('/salle/getSalleCours/<idCours>', methods=['GET','POST'])
@jwt_required()
def get_salle_cours(idCours):
    """Renvoit la salle dans lequel se déroule le cours via la route /salle/getSalleCours/<idCours>
    
    :param idCours: id du cours à rechercher
    :type idCours: int
    
    :raises DonneeIntrouvableException: Aucune donnée n'a pas être trouvé correspondant aux critères
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la récupération des données
    
    :return: l'id de la salle dans lequel se déroule cours
    :rtype: json
    """
    if (not idCours.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idCours", "int"))}), 400
    
    query = f"select edt.salle.* from edt.salle inner join edt.accuellir  using(idSalle) inner join edt.cours using(idCours) where idCours={idCours} "
    returnStatement = []
    conn = connect_pg.connect()
    try:
        rows = connect_pg.get_query(conn, query)
        for row in rows:
            returnStatement.append(get_salle_statement(row))
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("accuellir", "récuperer"))}), 500
        
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)


@salle.route('/salle/delete/<idSalle>', methods=['DELETE'])
@jwt_required()
def delete_salle(idSalle):
    """Permet de supprimer une salle via la route /salle/delete/<idSalle>
    
    :param idSalle: id de la salle à supprimer
    :type idSalle: int

    :raises ActionImpossibleException: Impossible de supprimer la salle spécifié dans la table salle
    :raises ParamètreTypeInvalideException: Le type de idSalle est invalide, une valeur de type int est attendue
    
    :return: message de succès
    :rtype: str
    """
    if (not idSalle.isdigit()):
        return jsonify({'error': str(apiException.ParamètreTypeInvalideException("idSalle", "numérique"))}), 400
    
    query = f"delete from edt.salle where idSalle={idSalle}"
    query2 = f"delete from edt.accuellir where idSalle={idSalle}"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query2)
        returnStatement = connect_pg.execute_commands(conn, query)
        
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("salle","supprimé"))}), 500
    
    return jsonify({'success': 'salle supprimé'}), 200

@salle.route('/salle/add', methods=['POST'])
@jwt_required()
def add_salle():
    """Permet d'ajouter une salle via la route /salle/add
    
    :param salle: salle à ajouter, spécifié dans le body
    :type salle: json

    :raises ActionImpossibleException: Impossible d'ajouter la salle spécifié dans la table salle
    :raises DonneeExistanteException: Cette salle existe déjà
    :raises ParamètreBodyManquantException: Si le body est manquant
    
    :return: l'id de l'utilisateur crée
    :rtype: json
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException())}), 400

    query = f"Insert into edt.salle (Nom, Capacite) values ('{json_data['Nom']}',{json_data['Capacite']}) returning idSalle"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
        idSemestre = returnStatement
    except Exception as e:
        if e.pgcode == errorcodes.UNIQUE_VIOLATION:
            # Erreur violation de contrainte unique
            return jsonify({'error': str(
                apiException.DonneeExistanteException(json_data['Nom'], "Nom", "salle"))}), 400
        else:
            # Erreur inconnue
            return jsonify({'error': str(apiException.ActionImpossibleException("salle"))}), 500

    return jsonify({"success" : "la salle a été ajouté" , "idSalle" : returnStatement }), 200



##################    Equipement de Salle    ####################
# TODO: Delete
@salle.route('/salle/get/equipement/<idSalle>', methods=['GET'])
@jwt_required()
def get_equipements_of_salle(idSalle):
    """Renvoit tous les salles au quel l'equipement(avec l'idEquipement) est lié via la route /salle/get/equipement/<idSalle>

    :param idSalle: l'id d'un groupe présent dans la base de donnée
    :type idSalle: str

    :raises PermissionManquanteException: L'utilisatuer n'a pas les droits pour avoir accés à cette route
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de la récupération des données
    
    :return: tous les equipements d'une salle
    :rtype: json
    """
    conn = connect_pg.connect()
    permision = perm.getUserPermission(get_jwt_identity() , conn)[0]

    if(permision == 3):
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403

    query = f"SELECT equipement.* from edt.equiper AS e NATURAL JOIN edt.equipement AS equipement WHERE e.idSalle={idSalle}"

    returnStatement = []
    try:
        equipements = connect_pg.get_query(conn, query)
        if equipements == []:
            return jsonify([])
        for row in equipements:
            returnStatement.append(get_equipement_statement(row))
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("salle", "récuperer"))}), 500
    connect_pg.disconnect(conn)
    return jsonify(returnStatement)
    
   

@salle.route('/salle/add/equipement/<idSalle>', methods=['POST'])
@jwt_required()
def add_equipements_of_salle(idSalle):
    """Permet d'ajouter une ou plusieurs salles a un équipement via la route /salle/add/equipement/<idSalle>

    :param idSalle: l'id d'un groupe présent dans la base de donnée
    :type idSalle: str

    :raises PermissionManquanteException: L'utilisatuer n'a pas les droits pour avoir accés à cette route
    :raises ParamètreBodyManquantException: Si le body est manquant
    :raises ActionImpossibleException: Si une erreur inconnue est survenue lors de l'insertion des données

    :return: un tableau d'id d'equipement crééent
    :rtype: json
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException())}), 400

    conn = connect_pg.connect()
    permision = perm.getUserPermission(get_jwt_identity() , conn)[0]

    if not (perm.permissionCheck(get_jwt_identity(), 0 , conn)):
        return jsonify({'error': str(apiException.PermissionManquanteException())}), 403
    query = "INSERT INTO edt.equiper (idSalle, idEquipement) VALUES "
    value_query = []

    for data in json_data['idEquipement']:
        value_query.append(f"({idSalle},'{data}')")

    query += ",".join(value_query) + " returning idEquipement"

    # TODO: find why only one id is return when multiple one are inserted
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except(Exception) as e:
        return jsonify({'error': str(apiException.ActionImpossibleException("groupe", "récuperer"))}), 500
    # TODO: handle error pair of key already exist
    connect_pg.disconnect(conn)
    return jsonify({"success": f"The equipements with the ids {returnStatement} were successfully created"}), 200    #{', '.join(tabIdEquipement)}


@salle.route('/salle/update', methods=['PUT'])
@jwt_required()
def update_salle():
    """Permet de modifier une salle via la route /salle/update
    
    :param salle: salle à modifier, spécifié dans le body
    :type salle: json

    :raises InsertionImpossibleException: Impossible de modifier la salle spécifié dans la table salle
    :raises ParamètreBodyManquantException: Si le body est manquant
    
    :return: message de succès
    :rtype: str
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({'erreur': str(apiException.ParamètreBodyManquantException())}), 400
    query = f"update edt.salle set Nom='{json_data['Nom']}', Capacite={json_data['Capacite']} where idSalle={json_data['idSalle']}"
    conn = connect_pg.connect()
    try:
        returnStatement = connect_pg.execute_commands(conn, query)
    except psycopg2.IntegrityError as e:
        return jsonify({'error': str(apiException.InsertionImpossibleException("salle"))}), 500
    return jsonify({'success': 'salle modifié'}), 200

