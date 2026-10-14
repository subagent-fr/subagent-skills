---
name: prospection-encadree
description: "Écrire à une liste de contacts professionnels depuis une boîte Subagent Mail sans abîmer la réputation du domaine. À utiliser quand l'humain donne plusieurs destinataires d'un coup (prospection, relances, invitations, prise de contact) : préparer un message par personne, tout laisser en brouillon, tenir compte du quota et des limites d'essai, ne pas doubler, puis rendre compte. Ne pas utiliser pour un seul message (envoyer-un-email) ni pour des envois en masse, que Subagent Mail ne fait pas."
---

# Écrire à une liste

Subagent Mail n'est pas un outil d'envoi en masse : une boîte écrit 5 e-mails par jour la première semaine, puis 10, 15 et 20. Une liste se traite sur plusieurs jours. Le serveur étale et retient de lui-même ; votre travail est d'écrire juste et de dire à votre humain ce qui va réellement se passer.

## 1. Mesurer avant de promettre

Appelez `inbox_status`. Lisez pour la boîte : le quota restant aujourd'hui (`quota`), les messages déjà en file (`queued`), et les limites d'essai de l'espace (`trial`), s'il en a.

Dites à votre humain, avant d'écrire, combien de messages partiront aujourd'hui et sur combien de jours la liste s'étalera. Sur une boîte du domaine commun `subagentmail.fr` : 3 destinataires distincts au plus la première heure, 5 le premier jour, 10 la première semaine. Si la liste dépasse ce que la boîte peut faire dans le délai voulu, dites-le maintenant.

## 2. Nettoyer la liste

- Un message par personne, à une adresse professionnelle en rapport avec le métier du destinataire.
- Retirez les doublons de la liste.
- Vérifiez les adresses déjà bloquées avec `list_suppressions` (`query` prend une adresse ou un domaine). Ne leur écrivez pas.
- Si la boîte a déjà écrit à quelqu'un, c'est une relance : elle se fait dans son fil, avec `reply_to_thread`.

**`list_suppressions`** (permission `read`). Liste les adresses et domaines bloqués pour cet espace (désinscriptions, plaintes, ajouts manuels), les plus récents d’abord.

| Paramètre | Type | Obligatoire | Description |
| --- | --- | --- | --- |
| `query` | texte | non | Une partie d’adresse ou de domaine ; une adresse complète pour savoir si elle est morte. |
| `cursor` | texte | non | Curseur de la page suivante : la valeur next_cursor de l’appel précédent. |
| `limit` | entier | non | Nombre d’éléments rendus (20 par défaut). |

## 3. Écrire, en brouillon

Pour chaque destinataire, appelez `send_email` avec :

- un texte écrit pour cette personne. Aucun champ entre doubles accolades ne doit rester (`unresolved_placeholder`) ;
- `requires_approval` à vrai : votre humain relit avant que quoi que ce soit ne parte ;
- une `idempotency_key` propre au destinataire et à la campagne (par exemple `invitation-salon-nadia.morel@exemple.com`) : si vous êtes interrompu, vous reprenez sans doubler.

**`send_email`** (permission `send`). Écrit un premier message à un destinataire depuis une boîte.

| Paramètre | Type | Obligatoire | Description |
| --- | --- | --- | --- |
| `inbox_id` | texte | oui | Boîte d’envoi (inb_…, voir list_inboxes). |
| `to` | texte | oui | Adresse du destinataire. |
| `subject` | texte | oui | Sujet (une ligne). |
| `text` | texte | oui | Texte brut du message (obligatoire). Écrivez {{unsubscribe_url}} pour placer vous-même le lien de désinscription ; sinon Subagent ajoute une mention en pied, tant que le correspondant n’a pas écrit dans le fil. Aucun autre {{champ}} n’est accepté : remplacez-les avant. |
| `to_name` | texte | non | Nom du destinataire, facultatif. |
| `test` | booléen | non | Envoi de test, à soi-même seulement (l’e-mail de l’humain de l’espace ou une autre boîte de l’espace) : pas de règle de doublon, et son lien de désinscription ne désinscrit personne. |
| `from_address` | texte | non | Adresse principale ou alias autorisé de la boîte (list_inboxes). |
| `html` | texte | non | Version HTML facultative, même contenu que text. |
| `reply_to` | texte | non | Adresse de réponse, si elle diffère de la boîte. |
| `metadata` | objet | non | Données libres de l’agent (8 000 caractères au plus), rendues telles quelles dans les lectures et les webhooks. |
| `requires_approval` | booléen | non | true : le message reste brouillon jusqu’à ce qu’un humain le valide (approve_message). Certains espaces l’imposent toujours. |
| `send_after` | texte | non | Pas avant cette date (ISO 8601, ou heure de Paris sans fuseau). Le créneau (sauf pour une réponse dans une conversation) et les quotas s’appliquent ensuite. |
| `idempotency_key` | texte | non | Clé unique de cet envoi (1 à 255 caractères). Rejouer la même clé avec le même contenu rend le message déjà créé ; avec un contenu différent, refus explicite. Recommandée pour tout réessai. |

Le lien de désinscription est ajouté par le serveur à chaque message. Ne l'enlevez pas, ne le remplacez pas par une formule.

Faites un premier lot court (trois à cinq messages) et montrez-le à votre humain avant d'écrire la suite : une erreur de ton se corrige sur trois brouillons, pas sur cinquante.

## 4. Ce qui est refusé, et ce qui attend

Un refus pour un destinataire n'arrête pas la liste : notez-le et passez au suivant. Ne réessayez pas avec une autre boîte ou une autre orthographe de l'adresse.

| `code` | HTTP | Ce qui s'est passé | Que faire |
| --- | --- | --- | --- |
| `recipient_suppressed` | 422 | Le destinataire est bloqué : désinscription, plainte, adresse morte ou blocage manuel. | Ne plus écrire à cette adresse, depuis aucune boîte. |
| `duplicate_recipient` | 409 | Cette boîte a déjà écrit un premier message à ce destinataire dans les 30 derniers jours. | Répondre dans le fil donné par la piste, avec `reply_to_thread`. |
| `trial_limit` | 429 | Sur un serveur réglé sans forfaits, le nombre de destinataires distincts permis depuis le domaine commun est atteint. | Suivre la piste : elle donne le moment où l'envoi reprend. |
| `key_daily_cap` | 429 | Le plafond de messages par jour de la clé est atteint. | Reprendre le lendemain, à partir de 0 h, heure de Paris. |
| `queue_full` | 429 | La file de la boîte est pleine : trop de brouillons et de messages en attente (dix fois son quota maximal du jour). | Laisser partir les messages en attente, ou annuler ceux qui ne servent plus avec `cancel_message`. |
| `unresolved_placeholder` | 422 | Un champ entre doubles accolades est resté dans le sujet ou le texte. | Remplacer chaque champ par sa valeur. Seul `{{unsubscribe_url}}` est accepté. |
| `inbox_suspended` | 409 | Le coupe-circuit a suspendu la boîte. La raison est dans le message. | Vérifier la liste de destinataires. La reprise est manuelle, par un administrateur de Subagent : l'humain la demande avec `request_inbox_review`. |

Un message en file (`queued`) n'est pas refusé : il attend son créneau. Ne le renvoyez pas.

Si la boîte est suspendue (`inbox_suspended`), arrêtez tout : trop de messages sont revenus ou ont été signalés. La liste est à revoir avec votre humain avant d'écrire un mot de plus.

## 5. Rendre compte

Donnez à votre humain un compte exact :

- combien de brouillons l'attendent, et où les relire (son assistant, avec une clé qui porte `approve`) ;
- qui a été écarté, et pourquoi : déjà bloqué, déjà contacté, adresse refusée ;
- quand les messages partiront une fois validés : le quota du jour, le créneau, le nombre de jours.

Ne dites jamais « envoyé » pour un brouillon ou un message en file.

## 6. Ensuite

Les réponses arrivent dans les fils de la boîte : `list_threads` avec `status` à `replied`. Une personne qui demande à ne plus être contactée se bloque avec `add_suppression`. Une relance se fait dans le fil, avec `reply_to_thread`, et seulement si votre humain la demande.
