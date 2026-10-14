---
name: envoyer-un-email
description: "Écrire un e-mail depuis une boîte Subagent Mail, par le serveur MCP. À utiliser pour TOUTE demande d'envoi, même un message d'une ligne : premier message à quelqu'un (send_email), réponse ou relance dans un fil (reply_to_thread), brouillon à faire valider, envoi de test, envoi différé, annulation (cancel_message). Les règles d'envoi valent quelle que soit la taille de la tâche. Ne pas utiliser pour lire les réponses (suivre-les-reponses) ni pour valider un brouillon au nom de l'humain (valider-les-brouillons)."
---

# Envoyer un e-mail

## Choisir l'outil

- **Première fois que cette boîte écrit à cette personne** : `send_email`. Il n'accepte pas de `thread_id`.
- **Il existe déjà un fil avec elle** (réponse ou relance) : `reply_to_thread`, avec le `thread_id` du fil. Écrire une seconde fois par `send_email` est refusé : `duplicate_recipient`.

Un message a un seul destinataire. Pas de pièce jointe.

## Avant d'écrire

1. Appelez `inbox_status` si vous ne l'avez pas fait dans cette session : il donne l'identifiant de la boîte (`inbox_id`), le quota restant et si l'espace impose la validation (`require_approval`).
2. N'inventez ni destinataire, ni promesse, ni signature. Ce que votre humain n'a pas dit, demandez-le.
3. « Écris », « prépare », « rédige » : c'est un brouillon. Passez `requires_approval` à vrai. « Envoie » : c'est un envoi, si la boîte, le destinataire, le sujet et le texte sont connus.

## Écrire

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

**`reply_to_thread`** (permission `send`). Répond dans un fil existant, au correspondant du fil : sujet « Re: … » et en-têtes In-Reply-To / References corrects, pour que la réponse s’affiche dans la même conversation chez le destinataire.

| Paramètre | Type | Obligatoire | Description |
| --- | --- | --- | --- |
| `thread_id` | texte | oui | Le fil (thr_…, voir list_threads). |
| `text` | texte | oui | Texte brut du message (obligatoire). Écrivez {{unsubscribe_url}} pour placer vous-même le lien de désinscription ; sinon Subagent ajoute une mention en pied, tant que le correspondant n’a pas écrit dans le fil. Aucun autre {{champ}} n’est accepté : remplacez-les avant. |
| `subject` | texte | non | Sujet, facultatif : « Re: » + sujet du fil par défaut. |
| `cc` | liste | non | Adresses en copie : seulement si le correspondant a déjà écrit dans le fil, vers quelqu’un qui y a lui aussi écrit ou une adresse de l’espace. |
| `from_address` | texte | non | Adresse principale ou alias autorisé de la boîte (list_inboxes). |
| `html` | texte | non | Version HTML facultative, même contenu que text. |
| `reply_to` | texte | non | Adresse de réponse, si elle diffère de la boîte. |
| `metadata` | objet | non | Données libres de l’agent (8 000 caractères au plus), rendues telles quelles dans les lectures et les webhooks. |
| `requires_approval` | booléen | non | true : le message reste brouillon jusqu’à ce qu’un humain le valide (approve_message). Certains espaces l’imposent toujours. |
| `send_after` | texte | non | Pas avant cette date (ISO 8601, ou heure de Paris sans fuseau). Le créneau (sauf pour une réponse dans une conversation) et les quotas s’appliquent ensuite. |
| `idempotency_key` | texte | non | Clé unique de cet envoi (1 à 255 caractères). Rejouer la même clé avec le même contenu rend le message déjà créé ; avec un contenu différent, refus explicite. Recommandée pour tout réessai. |

- **`text` est obligatoire.** `html` est facultatif et doit dire la même chose.
- **Le lien de désinscription est ajouté par le serveur.** Pour le placer vous-même, écrivez `{{unsubscribe_url}}` dans le texte. Aucun autre champ entre doubles accolades n'est accepté : remplacez-les avant, sinon l'envoi est refusé (`unresolved_placeholder`).
- **`idempotency_key`** : passez-en une à chaque envoi, propre à ce message (par exemple `relance-dupont-2026-10-13`). Si vous devez réessayer, reprenez la même.
- **`test`** : un envoi de test ne part qu'à l'humain de l'espace ou à une autre boîte de l'espace.
- **`send_after`** : pas avant cette date. Le créneau et les quotas s'appliquent ensuite.

## Lire la réponse

Le résultat porte `message`, `thread`, `inbox`, `estimated_send_at` et `replayed`. Regardez `status` dans `message` :

| `status` | Ce que cela veut dire | Que faire |
| --- | --- | --- |
| `queued` | Le message est en file. Il partira dans le créneau, selon le quota de la boîte. | Rien. Donnez à votre humain l'heure de `estimated_send_at`. **Ne le renvoyez pas.** |
| `draft` | Il attend une validation humaine. | Dites à votre humain qu'un brouillon l'attend. Vous ne pouvez pas le valider. |

`replayed` à vrai : la même `idempotency_key` avait déjà servi pour ce contenu, rien de nouveau n'a été créé.

Dites toujours à votre humain ce qui s'est réellement passé : « en file, départ au plus tôt lundi 9 h » n'est pas « envoyé ».

## Corriger ou annuler

- Un brouillon se corrige avec `update_draft` (sujet, texte, HTML). Le destinataire et la boîte ne changent pas : annulez et recommencez.
- Un brouillon ou un message encore en file s'annule avec `cancel_message`. Un message parti ne se rappelle pas : `not_cancellable`.

## Quand le serveur refuse

Faites ce que dit la piste (`hint`). Ne contournez jamais un refus en changeant de boîte ou d'adresse.

| `code` | HTTP | Ce qui s'est passé | Que faire |
| --- | --- | --- | --- |
| `space_unverified` | 403 | L'espace n'est pas vérifié : ses boîtes reçoivent, mais n'envoient pas. | Demander à l'humain le code à 6 chiffres, puis appeler `verify`. S'il n'a rien reçu, ou si aucun e-mail n'est rattaché à l'espace : `attach_human`. |
| `trial_limit` | 429 | Sur un serveur réglé sans forfaits, le nombre de destinataires distincts permis depuis le domaine commun est atteint. | Suivre la piste : elle donne le moment où l'envoi reprend. |
| `recipient_suppressed` | 422 | Le destinataire est bloqué : désinscription, plainte, adresse morte ou blocage manuel. | Ne plus écrire à cette adresse, depuis aucune boîte. |
| `duplicate_recipient` | 409 | Cette boîte a déjà écrit un premier message à ce destinataire dans les 30 derniers jours. | Répondre dans le fil donné par la piste, avec `reply_to_thread`. |
| `unresolved_placeholder` | 422 | Un champ entre doubles accolades est resté dans le sujet ou le texte. | Remplacer chaque champ par sa valeur. Seul `{{unsubscribe_url}}` est accepté. |
| `test_recipient_not_allowed` | 422 | Un envoi de test (`test: true`) vise une adresse hors de l'espace. | Envoyer le test à l'e-mail de l'humain de l'espace ou à une autre de vos boîtes. Pour écrire à ce destinataire : retirer `test`. |
| `key_daily_cap` | 429 | Le plafond de messages par jour de la clé est atteint. | Reprendre le lendemain, à partir de 0 h, heure de Paris. |
| `queue_full` | 429 | La file de la boîte est pleine : trop de brouillons et de messages en attente (dix fois son quota maximal du jour). | Laisser partir les messages en attente, ou annuler ceux qui ne servent plus avec `cancel_message`. |
| `inbox_suspended` | 409 | Le coupe-circuit a suspendu la boîte. La raison est dans le message. | Vérifier la liste de destinataires. La reprise est manuelle, par un administrateur de Subagent : l'humain la demande avec `request_inbox_review`. |
| `domain_not_verified` | 409 | Le domaine de la boîte n'est pas encore vérifié. | Publier ses enregistrements DNS, puis appeler `verify_domain`. |
| `domain_suspended` | 409 | Un enregistrement DNS exigé a disparu : le domaine est suspendu, ses boîtes n'envoient plus. | Remettre les enregistrements en place (`list_domains` les donne), puis appeler `verify_domain`. |
| `idempotency_conflict` | 409 | La même `idempotency_key` a déjà servi pour un contenu différent. | Même message : réutiliser la clé telle quelle. Nouveau message : en prendre une nouvelle. |
| `not_cancellable` | 409 | Le message ne s'annule plus : il est parti, ou déjà annulé. | Rien : un message parti ne se rappelle pas. |
