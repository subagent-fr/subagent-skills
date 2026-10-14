---
name: envoyer-de-son-domaine
description: "Enregistrer le domaine de l'humain dans Subagent Mail pour que les boîtes de l'agent portent son nom et sortent des limites d'essai. À utiliser pour add_domain, la publication des enregistrements DNS (preuve de propriété, DKIM, SPF, MX, DMARC), verify_domain, list_domains, remove_domain, et pour créer ou supprimer une boîte (create_inbox, delete_inbox). À utiliser aussi quand un envoi est refusé parce que le domaine n'est pas vérifié ou qu'il est suspendu."
---

# Envoyer de son domaine

Une boîte ouverte par `sign_up` vit sur le domaine commun d'essai `subagentmail.fr`, avec des limites d'essai. Pour en sortir, l'espace enregistre son propre domaine. Il faut un espace vérifié et une clé qui porte `manage_inboxes`.

## En trois temps

### 1. Enregistrer

Demandez le domaine à votre humain. **Conseillez un sous-domaine** (par exemple `agents.exemple.fr`) si le domaine reçoit déjà du courrier ailleurs : l'enregistrement MX fait arriver tout le courrier du domaine enregistré dans les boîtes Subagent.

Appelez `add_domain`. Il rend `records` : la liste exacte des enregistrements DNS à publier.

**`add_domain`** (permission `manage_inboxes`). Enregistre le domaine d’où votre espace veut envoyer (le vôtre, ou un sous-domaine comme agents.exemple.fr) et rend la liste exacte des enregistrements DNS à publier chez l’hébergeur du domaine : preuve de propriété, deux clés DKIM, SPF, MX, et DMARC conseillé.

| Paramètre | Type | Obligatoire | Description |
| --- | --- | --- | --- |
| `domain` | texte | oui | Le nom de domaine, par exemple exemple.fr ou agents.exemple.fr. |

**`verify_domain`** (permission `manage_inboxes`). Contrôle dans le DNS les enregistrements du domaine et rend l’état de chacun : trouvé, absent, ou valeur différente (avec la valeur vue).

| Paramètre | Type | Obligatoire | Description |
| --- | --- | --- | --- |
| `domain` | texte | oui | Le domaine à contrôler (voir list_domains). |

**`list_domains`** (permission `manage_inboxes` ou `read`). Liste les domaines enregistrés par cet espace, avec leur état (en attente, vérifié, suspendu), leurs enregistrements DNS à publier et ce qui a été vu au dernier contrôle.

Aucun paramètre.

**`remove_domain`** (permission `manage_inboxes`). Retire un domaine de l’espace : plus aucune boîte ne s’y crée, et le serveur de messagerie cesse de recevoir son courrier.

| Paramètre | Type | Obligatoire | Description |
| --- | --- | --- | --- |
| `domain` | texte | oui | Le domaine à retirer (voir list_domains). |
| `confirm` | booléen | oui | Doit valoir true : le retrait est irréversible. |

### 2. Publier

C'est le seul geste qui se fait hors de l'assistant : votre humain publie les enregistrements chez l'hébergeur DNS du domaine. Donnez-les-lui tels que le serveur les rend, un par un : `type`, `name`, `value`. Ne les recopiez pas de mémoire et ne les abrégez pas.

| `role` | Exigé | À savoir |
| --- | --- | --- |
| `ownership` | oui | La preuve que le domaine est à lui. |
| `dkim` | oui | Deux clés : publiez les deux. |
| `spf` | oui | Un domaine n'a qu'un enregistrement SPF. S'il en a déjà un, il faut le compléter, pas en créer un second : la note de l'enregistrement dit comment. |
| `mx` | oui | Le courrier du domaine arrive alors dans les boîtes Subagent. |
| `dmarc` | non | Conseillé. |

Chaque enregistrement porte `required` et, quand il y a lieu, une `note` : lisez-la à votre humain.

### 3. Vérifier

Appelez `verify_domain`. Il rend l'état de chaque enregistrement (`state`) : `found`, `missing`, ou `different` avec la valeur vue (`seen`). Dites à votre humain lequel corriger, avec la valeur attendue et la valeur vue.

Un changement de DNS met parfois quelques minutes à se voir. Ne rappelez pas `verify_domain` en boucle : plus de six appels par minute sont refusés (`rate_limited`). Attendez, puis rappelez.

Quand `status` vaut `verified`, créez les boîtes.

## Créer une boîte

`create_inbox` avec `username`, `display_name` (le nom affiché dans « De : ») et `domain`.

**`create_inbox`** (permission `manage_inboxes`). Crée une boîte e-mail <username>@<domaine> sur un domaine d’envoi de l’espace (son propre domaine vérifié, voir add_domain ; sinon le domaine commun ou celui de la marque), et le compte correspondant sur le serveur de messagerie.

| Paramètre | Type | Obligatoire | Description |
| --- | --- | --- | --- |
| `username` | texte | oui | Partie avant @ (minuscules, chiffres, . _ -), par exemple « prospection » ou « marie.durand ». Sur le domaine commun : 3 à 32 caractères, et une adresse déjà attribuée ne se réattribue pas. |
| `display_name` | texte | oui | Nom affiché dans « De : », par exemple « Marie de Prescriptio ». |
| `domain` | texte | non | Domaine d’envoi de l’espace. Absent : son premier domaine, le sien d’abord s’il en a un de vérifié (voir inbox_status, tenant.domains). |

**`delete_inbox`** (permission `manage_inboxes`). Supprime une boîte : ses brouillons et messages en file sont annulés, et le compte de messagerie est supprimé s’il a été créé par Subagent (une boîte rattachée par un administrateur de Subagent est seulement détachée).

| Paramètre | Type | Obligatoire | Description |
| --- | --- | --- | --- |
| `inbox_id` | texte | oui | La boîte à supprimer (inb_…). |
| `confirm` | booléen | oui | Doit valoir true : la suppression est irréversible. |

Chaque boîte neuve commence sa montée progressive : 5 e-mails par jour la première semaine, puis 10, 15 et 20. Vous ne pouvez ni la lever ni l'accélérer. Dites-le à votre humain avant qu'il ne compte sur un volume.

Ne supprimez pas une boîte pour en recréer une : les créations sont comptées sur sept jours, boîtes supprimées comprises (`inbox_creation_limit`).

## Supprimer

`delete_inbox` et `remove_domain` sont irréversibles et demandent `confirm` à vrai. Ne les appelez que sur demande explicite de votre humain, après lui avoir redit l'adresse ou le domaine exact. Un domaine qui porte encore des boîtes ne se retire pas (`domain_in_use`).

## Si le domaine est suspendu

Un domaine vérifié est recontrôlé. Si un enregistrement exigé disparaît, il passe à `suspended` et ses boîtes n'envoient plus. `list_domains` donne les enregistrements attendus et ce qui a été vu : faites-les remettre, puis appelez `verify_domain`.

## Quand le serveur refuse

| `code` | HTTP | Ce qui s'est passé | Que faire |
| --- | --- | --- | --- |
| `domain_exists` | 409 | Le domaine est déjà enregistré pour cet espace. | Appeler `list_domains` : il donne ses enregistrements DNS et son état. |
| `domain_taken` | 409 | Un autre espace a déjà prouvé la propriété de ce domaine. | Enregistrer un sous-domaine, ou demander à un administrateur de Subagent de le libérer. |
| `domain_limit` | 409 | Le plafond de cinq domaines par espace est atteint. | Retirer un domaine inutile avec `remove_domain`. |
| `public_mail_domain` | 422 | Une messagerie publique (`gmail.com`…) ne se bloque pas en entier, et ne s'enregistre pas comme domaine. | Bloquer les adresses une à une. Enregistrer un domaine dont vous gérez le DNS. |
| `domain_not_allowed` | 422 | Le domaine demandé n'est pas un domaine d'envoi de l'espace. Ou, pour `add_domain`, c'est un domaine de Subagent. | Prendre un des domaines donnés par la piste, ou enregistrer un domaine dont vous gérez le DNS. |
| `dns_unavailable` | 503 | La résolution DNS a échoué : rien n'a pu être contrôlé. | Réessayer dans un instant. L'état du domaine n'a pas changé. |
| `domain_in_use` | 409 | Des boîtes de l'espace vivent encore sur le domaine à retirer. | Supprimer d'abord ces boîtes avec `delete_inbox`. |
| `domain_not_verified` | 409 | Le domaine de la boîte n'est pas encore vérifié. | Publier ses enregistrements DNS, puis appeler `verify_domain`. |
| `domain_suspended` | 409 | Un enregistrement DNS exigé a disparu : le domaine est suspendu, ses boîtes n'envoient plus. | Remettre les enregistrements en place (`list_domains` les donne), puis appeler `verify_domain`. |
| `address_taken` | 409 | L'adresse est déjà une boîte. | Choisir un autre `username`. |
| `inbox_limit` | 409 | Le plafond de boîtes du forfait est atteint. La piste donne le nombre de boîtes et le prix du forfait suivant. | Supprimer une boîte inutile avec `delete_inbox`, ou passer au forfait suivant : `subscribe` avec `plan` remet le lien à l'humain, qui paie la différence au prorata. Voir [Prix et paiement](/docs/prix#plus-grand). |
| `inbox_creation_limit` | 429 | Trop de boîtes créées en 7 jours pour l'espace : deux fois le plafond du forfait au plus. Les boîtes supprimées comptent. | Garder ses boîtes plutôt que les supprimer et les recréer. Pour un besoin réel, écrire à `contact@subagent.fr`. |
| `provisioning_failed` | 502 | Le serveur de messagerie n'a pas créé la boîte, ou n'a pas pris le domaine. | Réessayer dans un instant. Rien n'est perdu. |
