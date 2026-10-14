---
name: valider-les-brouillons
description: "Relire, corriger, valider ou refuser les brouillons qu'un agent a préparés dans Subagent Mail, au nom de l'humain et à sa demande. À utiliser quand l'humain dit « montre-moi les brouillons », « valide le premier », « corrige et envoie », « annule celui-là ». Demande une clé qui porte la permission approve : c'est l'assistant de l'humain qui s'en sert, pas l'agent qui a écrit les messages. Ne jamais utiliser de sa propre initiative."
---

# Valider les brouillons

La validation est un geste humain. Vous ne validez un brouillon que sur demande explicite de votre humain, pour ce brouillon-là, après qu'il en a vu le texte. « Occupe-toi des e-mails » n'est pas une demande de validation.

## Vérifier que vous pouvez valider

`approve_message` demande la permission `approve`. La clé qu'un agent reçoit de `sign_up` ne la porte pas : s'il s'agit de cette clé, vous ne pouvez pas valider, et c'est voulu. `inbox_status` rend les permissions de la clé (`key`).

Si l'appel est refusé avec le code `forbidden`, dites-le simplement à votre humain. Ne cherchez pas une autre voie.

## Montrer ce qui attend

`list_drafts` rend les brouillons à valider, avec leur texte complet, les plus récents d'abord.

**`list_drafts`** (permission `read` ou `approve`). Liste les brouillons qui attendent une validation humaine, avec leur texte complet, les plus récents d’abord.

| Paramètre | Type | Obligatoire | Description |
| --- | --- | --- | --- |
| `inbox_id` | texte | non | Une seule boîte (inb_…). |
| `cursor` | texte | non | Curseur de la page suivante : la valeur next_cursor de l’appel précédent. |
| `limit` | entier | non | Nombre d’éléments rendus (20 par défaut). |

Montrez à votre humain, pour chaque brouillon : la boîte d'envoi (`from`), le destinataire (`to`), le sujet, le texte en entier, l'adresse de réponse si elle diffère (`reply_to`) et s'il a une version HTML (`has_html`). Ne résumez pas un texte qu'il doit approuver : il valide ce qu'il a lu.

Gardez la `revision` de chaque brouillon lu.

## Valider

Appelez `approve_message` avec `message_id` et la `revision` lue. Le message passe en file et partira dans le créneau, selon le quota de la boîte : dites « validé, en file », pas « envoyé ».

**`approve_message`** (permission `approve`). Validation humaine : le brouillon passe en file et partira dans le créneau, selon les quotas.

| Paramètre | Type | Obligatoire | Description |
| --- | --- | --- | --- |
| `message_id` | texte | oui | Le brouillon (msg_…, voir list_drafts). |
| `revision` | texte | non | La version du brouillon tel qu’il a été lu (champ revision de list_drafts). S’il a changé depuis, la validation est refusée (draft_changed). |

**`update_draft`** (permission `send` ou `approve`). Modifie le sujet, le texte ou le HTML d’un brouillon tant qu’il n’est pas validé.

| Paramètre | Type | Obligatoire | Description |
| --- | --- | --- | --- |
| `message_id` | texte | oui | Le brouillon (msg_…, voir list_drafts). |
| `subject` | texte | non | Nouveau sujet. |
| `text` | texte | non | Nouveau texte. |
| `html` | texte | non | Nouveau HTML (texte vide : retire la version HTML). |

**`cancel_message`** (permission `send` ou `approve`). Annule un brouillon ou un message encore en file : il ne partira pas.

| Paramètre | Type | Obligatoire | Description |
| --- | --- | --- | --- |
| `message_id` | texte | oui | Le message (msg_…). |
| `reason` | texte | non | Pourquoi, pour le journal. |

Si le brouillon a changé depuis la lecture, la validation est refusée (`draft_changed`) : relisez-le avec `list_drafts`, montrez la nouvelle version, redemandez.

Un lot (« valide-les tous ») se valide un par un, après que votre humain a vu chaque texte. S'il n'a vu qu'une liste de sujets, montrez d'abord les textes.

## Corriger

`update_draft` change le sujet, le texte ou le HTML. Montrez la version corrigée avant de valider : la correction change la `revision`. Le destinataire et la boîte ne se corrigent pas : annulez le brouillon et faites écrire un nouveau message.

## Refuser

`cancel_message` annule un brouillon ou un message encore en file. Donnez la raison dans `reason` : elle reste au journal du message.

## Quand le serveur refuse

| `code` | HTTP | Ce qui s'est passé | Que faire |
| --- | --- | --- | --- |
| `forbidden` | 403 | La clé ne porte pas la permission que l'outil demande. | Pour `approve` : le geste revient à l'humain, depuis son assistant branché à `https://api.subagent.fr/connect`. La piste le dit. |
| `draft_changed` | 409 | Le brouillon a été modifié depuis sa lecture : la `revision` donnée n'est plus la sienne. | Relire le brouillon avec `list_drafts`, puis valider la version lue. |
| `not_draft` | 409 | Le message n'est pas, ou n'est plus, un brouillon. | Relire son statut avec `get_message`. |
| `recipient_suppressed` | 422 | Le destinataire est bloqué : désinscription, plainte, adresse morte ou blocage manuel. | Ne plus écrire à cette adresse, depuis aucune boîte. |
| `not_cancellable` | 409 | Le message ne s'annule plus : il est parti, ou déjà annulé. | Rien : un message parti ne se rappelle pas. |
