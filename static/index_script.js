/** ----- Handsontable : création et paramétrage du tableau ----- **/

const data = [[]]; // Contenu du tableau
const container = document.getElementById('tableau'); // Récupération de la div où le tableau sera affiché
const hot = new Handsontable(container, {
    data: data,
    colWidth: 500,
    rowHeights: 30,
    width: '100%',
    height: 620,
    minRows: 20,
    minCols: 35,
    minSpareRows: 1,
    rowHeaders: true,
    viewportRowRenderingOffset: 200,
    colHeaders: true,
    colWidths: 100,
    contextMenu: true,
    language: 'fr-FR',
    filters: true,
    dropdownMenu: true,
    licenseKey: 'non-commercial-and-evaluation'
});


/** ----- API (Import) ----- **/

// Vérification que tous les champs requis sont remplis
function clearFields() {
    let file = document.forms["import-form"]["file"].value;
    let name = document.forms["import-form"]["table-name"].value;
    let yref = document.forms["import-form"]["year-ref"].value;
    if (file == null || name == null || name === "" || yref == null || yref === "") {
        return Boolean(false);
    }
    return Boolean(true);
}

// Vérification des erreurs potentielles suite au traitement du fichier par le serveur
function gestionErreurs(info, progress) {
    let msg = "";

    if (info === "err_ext" || info === "err_empty" || info === "err_com") {
        let filepath = document.getElementById("inputImportFile").value;
        let fileName = filepath.replace(/^.*?([^\\\/]*)$/, '$1');
        if (info === "err_ext") {
            msg = "L'extension du fichier \"" + fileName + "\" n'est pas supportée.";
        } else if (info === "err_empty") {
            msg = "Le fichier \"" + fileName + "\" est vide.";
        } else {
            msg = "Colonne avec les codes INSEE introuvable.\nAjoutez une colonne \"com\" avec les codes ou renommez la colonne correspondante.";
        }
        window.alert(msg);
        document.getElementById("inputImportFile").value = "";
        progress.css("visibility", "hidden");
        return -1;
    } else if (info === "err_name") {
        let tableName = document.getElementById("table-name").value;
        msg = "Le nom \"" + tableName + "\" est déjà utilisé."
        window.alert(msg);
        document.getElementById("table-name").value = "";
        progress.css("visibility", "hidden");
        return -1;
    } else if (info === "err_yearref") {
        let yearRef = document.getElementById("year-ref").value;
        let currentYear = new Date().getFullYear().toString().substr(-2);
        msg = "L'année 20" + yearRef + " est incorrecte.\nEntrez une année inférieure ou égale à l'année courante.";
        window.alert(msg);
        document.getElementById("year-ref").value = currentYear;
        progress.css("visibility", "hidden");
        return -1;
    }
    return 1;
}

// Fonction appelée à la soumission du formulaire d'import
async function submitImportForm(event) {
    event.preventDefault(); // Empêche le navigateur de recharger la page

    // Si un champ requis est vide, l'import ne s'effectue pas
    if (!clearFields()) {
        return;
    }

    const form = event.currentTarget;
    const url = form.action;
    const formData = new FormData(form);

    // Envoi du contenu du formulaire au serveur
    const response = await fetch(url, {
        method: "POST",
        body: formData
    });

    $("#import-modal").modal('hide');
    $("#operation-modal").modal('show');

    // Récupération du contenu du formulaire après le lien avec le refgéo et l'import dans la base de données
    const resp = await response.json();
    const info = JSON.parse(JSON.stringify(resp));
    const headers = Object.keys(info); // Récupération des noms de colonnes

    let results = [];
    results.push(headers);

    // Génération du dropdown selection du com
    let dropdown_com = await document.createElement("select");
    dropdown_com.setAttribute("id", "col_com");
    dropdown_com.setAttribute("name", "col_com");
    for (let j = 0; j < results[0].length; j++) {
        let option_com = await document.createElement("option");
        option_com.value = results[0][j];
        option_com.text = results[0][j];
        dropdown_com.appendChild(option_com);
    }
    document.getElementById("com-select").appendChild(dropdown_com);

    // Génération de la liste de dropdowns des opérations
    for (let i = 0; i < results[0].length; i++) {
        let element = await document.createElement("li");
        let header_name = await document.createTextNode(results[0][i]);
        let dropdown = await document.createElement("select");
        dropdown.setAttribute("id", "drpd_" + results[0][i]);
        dropdown.setAttribute("name", "drpd_" + results[0][i]);

        // Création des Options
        let option_1 = await document.createElement("option");
        option_1.value = "somme";
        option_1.text = "somme";
        let option_2 = await document.createElement("option");
        option_2.value = "max";
        option_2.text = "max";
        let option_3 = await document.createElement("option");
        option_3.value = "min";
        option_3.text = "min";
        // Selection de l'op par défaut
        let main_operator = await document.forms['import-form'].elements['drp_dwn_op'].value;
        switch (main_operator) {
            case option_3.value:
                option_3.selected = true;
                break;
            case option_2.value:
                option_2.selected = true;
                break;
            default:
                option_1.selected = true;
                break;
        }
        dropdown.appendChild(option_1);
        dropdown.appendChild(option_2);
        dropdown.appendChild(option_3);
        element.appendChild(header_name);
        element.appendChild(dropdown);
        document.getElementById("list-op").appendChild(element);
    }
}

async function submitSelectForm(event) {
    event.preventDefault(); // Empêche le navigateur de recharger la page

    $("#operation-modal").modal('hide');

    const form_select = event.currentTarget;
    const formSelect = new FormData(form_select);

    // Vide le champs fichier pour éviter de réimporter le fichier
    let file = document.getElementById("inputImportFile");
    const filename = file.value; // Récupère le nom du fichier pour le retrouver dans /temp
    file.value = "";

    const form_import = document.getElementById("import-form");
    let importData = new FormData(form_import);

    const url = form_select.action;

    importData.append("filename", filename);
    importData.delete('file');
    importData.append("formSelect", formSelect);

    for (let key of formSelect.entries()) {
       importData.append(key[0], key[1]);
    }

    const response = await fetch(url, {
        method: "POST",
        body: importData
    });

    const json = await response.json();
    const info = JSON.parse(JSON.stringify(json));

    // let info_ok = gestionErreurs(info, progress);
    // if (info_ok === -1) {
    //     return;
    // }

    let results = [];
    const headers = Object.keys(info); // Récupération des noms de colonnes
    const nbLines = Object.values(info[headers[0]]).length; // Récupération du nombre de lignes

    results.push(headers);

    // Réordonne le tableau du serveur pour coller au format de Handsontable
    for (let i = 0; i < nbLines; i++) {
        let resultLine = [];
        for (let header of headers) {
            resultLine.push(info[header][i]);
        }
        results.push(resultLine);
    }

    // Vide le formulaire de la pop up
    document.getElementById("import-form").reset();

    // Mets à jour le contenu du tableau
    hot.updateSettings({
        data: results,
    });
}

// Récupère le formulaire d'import dans l'HTML et ajoute un event listener
// qui déclenche la fonction submitImportForm en cas de clic sur bouton
const importForm = document.getElementById("import-form");
importForm.addEventListener("submit", submitImportForm);

const selectForm = document.getElementById("operation-form");
selectForm.addEventListener("submit", submitSelectForm);


/** ----- API (Export) ----- **/

// Nettoyage des données du tableau (à faire avant l'envoi au serveur)
function cleanData(data_unclean) {
    // Compte le nombre de colonne avec une en-tête
    let nb_columns = 0;
    const first_line = data_unclean[0];
    const data_size = data_unclean.length

    for (let i = 0; i < first_line.length; i++) {
        if (first_line[i] == null) {
            break;
        }
        nb_columns += 1;
    }

    // TODO : nettoyage data pour export : peut être possible de le faire en une seule fonction
    // Récupération des colonnes comprisent entre 0 et le nombre de colonne avec une en-tête
    let content_good_columns = [];

    for (let i = 0; i < data_size; i++) {
        content_good_columns[i] = data_unclean[i].slice(0, nb_columns);
    }

    // Récupération des lignes avec du contenu
    // S'arrête lorsqu'une ligne est vide
    let clean_content = []

    for (let i = 0; i < data_size; i++) {
        let liste_avec_elt = Boolean(false);
        for (let j = 0; j < content_good_columns[i].length; j++) {
            if (content_good_columns[i][j] != null) {
                liste_avec_elt = Boolean(true);
            }
        }
        if (liste_avec_elt) {
            clean_content.push(content_good_columns[i]);
        }
    }

    // Renvoie le tableau sans colonne ni ligne vide
    return clean_content
}

// Fonction permettant de télécharger un fichier CSV
function downloadFile(fileName, csv) {
    let encodedUri = encodeURI(csv); // Transformation des caractères spéciaux par leur version encodé en UTF-8
    let link = document.createElement("a"); // Création d'un nouveau lien qui lancera le téléchargement

    link.setAttribute("href", encodedUri); // Ajout du contenu du fichier
    link.setAttribute("download", fileName); // Fonction du lien : télécharger un fichier "fileName"

    document.body.appendChild(link); // Ajout du lien à la page

    link.click(); // Clic sur le lien, déclenche le téléchargement
}

// Fonction appelée suite au clic sur le bouton "Export"
async function exportToCSV(event) {
    event.preventDefault(); // Empêche le navigateur de recharger la page

    const progress = $("#import-progress"); // Récupération de la barre de progression
    progress.width("0%");
    $(".progress-bar").css("background-color", "#F79C16") // Colore la barre aux couleurs de l'export (#F79C16)
    progress.css("visibility", "visible"); // Affiche la barre
    progress.width("25%"); // Commence le chargement de la barre

    const url = window.location.href + "export"; // Récupération de l'URL d'export
    const data_csv = JSON.stringify(cleanData(hot.getData())); // Récupération des données du tableau
    progress.width("50%");

    // Envoie les données du tableau au serveur pour conversion en CSV
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: data_csv
    });
    progress.width("75%");

    // Récupération du CSV sous format texte
    const csv = await response.text();
    progress.width("100%");

    // Téléchargement du fichier
    downloadFile('export.csv', 'data:text/csv;charset=UTF-8,' + csv);

    // Cache la barre de progression
    setTimeout(function () {
        progress.css("visibility", "hidden");
    }, 500);
}

// Récupère le bouton d'export dans l'HTML et ajoute un event listener
// qui déclenche la fonction exportToCSV en cas de clic sur le bouton
const exportBtn = document.getElementById("btn-export");
exportBtn.addEventListener("click", exportToCSV);


/** OPERATIONS */
