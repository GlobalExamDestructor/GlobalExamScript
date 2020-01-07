# -*- coding: utf-8 -*-


"""
======================================== READ ME ========================================

Pour créer un .exe à partir de ce fichier, suivre ce tutoriel :
https://datatofish.com/executable-pyinstaller/

=========================================================================================
"""


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import random

temps_par_question = 60 # en secondes
coef_bonnes_réponses = 0.95 # part de bonnes réponses -> doit être compris entre 0(0%) et 1(100%)
navigateur = 1 # 1->Firefox, 2->Chrome
mail_utilisateur = " "
mdp_utilisateur = " "



def lire_données_utilisateur():
    global navigateur
    global mail_utilisateur
    global mdp_utilisateur
    global temps_par_question
    global coef_bonnes_réponses
    navigateur = int(input('Quel navigateur souhaites-tu utiliser ? [1->Firefox, 2->Chrome(version 79)] : '))
    print("[Tes identifiants sont requis pour la connexion automatique :]")
    mail_utilisateur = input('Ton email : ')
    mdp_utilisateur = input('Ton mot de passe Global Exam : ')
    temps_par_question = float(input('Combien de temps (en s) par question ? (40 recommandé) : '))
    coef_bonnes_réponses = float(input('Quelle part de bonnes réponses (de 0 à 1 [ex : 90% -> 0.9]) ? : '))





def se_connecter(identifiant, mdp):
    print("Connexion...")
    email = browser.find_element_by_id('email')
    email.send_keys(identifiant)
    mdp1 = browser.find_element_by_id('password')
    mdp1.send_keys(mdp)
    bouton = browser.find_element_by_id('login')
    bouton.click()
    print("Connecté")
    browser.get('https://upssitech.globalexam.training/study-plans')
    time.sleep(2)
    bouton = browser.find_element_by_class_name("full-card")
    bouton.click()
    




def prochain_exo(tps_par_quest, coef_b_rép):
    
    containers = browser.find_elements_by_class_name("row")
    
    on_a_trouvé_un_exo = False
    
    for i in range(1,len(containers)): # on évite le 0 car c'est un faux positif
        try:
          bouton = containers[i].find_element_by_class_name("exercise-item.cursor-pointer.exercise-active")
          print("Exo trouvé")
          try:
              texte = containers[i].find_element_by_class_name("activity-title.text-semibold")
              if "Examen" not in texte.text:
                  print("C'est un exo non fait")
                  on_a_trouvé_un_exo = True
                  bouton.click()
                  break
              else:
                  print("C'est un exam")
          except:
              pass # parce qu'on est obligé de mettre un except...
        except:
          pass
    
    if not on_a_trouvé_un_exo:
        return False
    
    print("C'est parti !")
    try: # au cas où il n'y ai pas de consignes
        bouton = browser.find_element_by_id('start_session')
        bouton.click()
    except:
        pass
    
    start_time = time.perf_counter()
    
    while 1: # on répond à toutes les questions jusqu'à arriver à la dernière page
        time.sleep(1)
        bout_petites_pages = browser.find_elements_by_class_name('page-link.py-1.border-0.rounded')
        num_petite_page_suivante = 2
        nb_petites_pages = len(bout_petites_pages)
        if nb_petites_pages == 0:
            nb_petites_pages += 1
        
        for n in range(nb_petites_pages):
            
            if len(bout_petites_pages) != 0:
                browser.execute_script("window.scrollTo(0, 0);") # on scroll jusqu'en haut
            
            bout_aff_rép = browser.find_elements_by_id('toggle_guidelines')
            for i in bout_aff_rép: # pour chaque bouton d'affichage de bonne réponse...
                i.click()
            
            réponses = {}
            bout_rép = browser.find_elements_by_class_name('custom-control.custom-radio.d-flex.align-items-center')
            
            for i in bout_rép: # pour chaque bouton réponse (correction comprise)...
                réponse = i.find_element_by_class_name('custom-control-input')
                if "correction" in réponse.get_attribute("name"):
                    rép_sans_corr = réponse.get_attribute("name").replace('correction_', '')
                    réponses[rép_sans_corr] = réponse.get_attribute("value")
            
            for i in bout_rép: # une fois qu'on connait les bonnes réponses, on reparcoure la liste
                réponse = i.find_element_by_class_name('custom-control-input')
                nom = réponse.get_attribute("name")
                if "correction" not in nom:
                    if réponses[nom] == réponse.get_attribute("value") and random.random() < coef_b_rép:
                        # si c'est la bonne réponse et qu'on a la "chance" de cliquer
                        i.find_element_by_class_name('custom-control-label').click()
            
            for i in bout_aff_rép: # on referme l'affichage des corrections
                i.click()
            
            if len(bout_petites_pages) != 0:
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);") # on scroll jusqu'en bas
            
            # si on est dans un exercice avec des "petites pages" dans chaque page :
            if len(bout_petites_pages) != 0 and num_petite_page_suivante <= len(bout_petites_pages):
                for k in bout_petites_pages:
                    if int(k.text) == num_petite_page_suivante:
                        k.click()
                        num_petite_page_suivante += 1
                        break
        
        try: # on essaie de cliquer sur le bouton 'suivant'
            bout_suivant = browser.find_element_by_id('next_part')
            bout_suivant.click()
            WebDriverWait(browser, 10).until(EC.url_changes(browser.current_url))
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "toggle_guidelines")))
        except: # sinon, c'est qu'on est à la dernière page, on quitte donc la boucle 'while 1'
            break
    
    nb_questions = 0
    titres_rép = browser.find_elements_by_class_name('mb-0')
    
    for i in reversed(titres_rép):
        if "Question" in i.text:
            nb_questions = int(i.text.replace('Question #', ''))
            break
    
    print("On laisse tourner le chrono...")
    print("(Durée de l'exercice : " + str(tps_par_quest * nb_questions / 60.0) + " minutes)")
    
    while (time.perf_counter() - start_time) < (tps_par_quest * nb_questions):
        time.sleep(1)
        # ainsi, on ne vérifie la condition que chaque seconde, ce qui consomme moins de ressources
    
    bout_terminer = browser.find_element_by_id('finish_session')
    bout_terminer.click()
    print("Exo terminer !")
    
    return True



# ================================ Début du programme ================================

lire_données_utilisateur()
print("Demarrage en cours...")

browser = None
if navigateur == 1:
    browser = webdriver.Firefox(executable_path = './geckodriver')
else:
    browser = webdriver.Chrome(executable_path = './chromedriver')
browser.get('https://upssitech.globalexam.training/fr/login')

se_connecter(mail_utilisateur, mdp_utilisateur)

exo_trouvé = True

while exo_trouvé:
    time.sleep(10) # pour laisser la page charger
    browser.get('https://upssitech.globalexam.training/study-plans')
    time.sleep(2)
    bouton = browser.find_element_by_class_name("full-card")
    bouton.click()
    try:
        exo_trouvé = prochain_exo(temps_par_question, coef_bonnes_réponses)
    except:
        pass

# while prochain_exo(temps_par_question, coef_bonnes_réponses):
#     time.sleep(10) # pour laisser la page charger
#     browser.get('https://upssitech.globalexam.training/study-plans')
#     time.sleep(2)
#     bouton = browser.find_element_by_class_name("full-card")
#     bouton.click()

browser.close()