################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides, implements
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.autoform import directives as form
from z3c.form.browser.select import SelectWidget

from zopyx.existdb import MessageFactory as _


def context_property(name):
    def getter(self):
        return getattr(self.context, name)
    def setter(self, value):
        setattr(self.context, name, value)
    def deleter(self):
        delattr(self.context, name)
    return property(getter, setter, deleter)


id2titles = {'acute-lymphoblastic-leukemia-all': 'Acute Lymphoblastic Leukemia (ALL)',
 'acute-promyelocytic-leukemia-apl': 'Acute Promyelocytic Leukemia (APL)',
 'adolescents-and-young-adults-aya': 'Adolescents and Young Adults (AYA)',
 'akute-lymphatische-leukaemie-all': 'Akute Lymphatische Leuk\xc3\xa4mie (ALL)',
 'akute-myeloische-leukaemie-2013-studien': 'Akute Myeloische Leuk\xc3\xa4mie \xe2\x80\x93 Studien',
 'akute-myeloische-leukaemie-aml': 'Akute Myeloische Leuk\xc3\xa4mie (AML)',
 'akute-promyelozytaere-leukaemie-apl': 'Akute Promyelozyt\xc3\xa4re Leuk\xc3\xa4mie (APL)',
 'akute-promyelozytaere-leukaemie-apl-studienergebnisse-phase-iii-studien-weitere-standard-setzende-studien-und-analysen': 'Akute Promyelozyt\xc3\xa4re Leuk\xc3\xa4mie (APL) - Studienergebnisse (Phase III Studien, weitere Standard-setzende Studien und Analysen)',
 'akute-promyelozytaere-leukaemie-apl-zulassungsstatus': 'Akute Promyelozyt\xc3\xa4re Leuk\xc3\xa4mie (APL) - Zulassungsstatus',
 'akute-promyelozytaere-leukaemie-studienergebnisse': 'Akute promyelozyt\xc3\xa4re Leuk\xc3\xa4mie - Studienergebnisse',
 'allgemeines-definition': 'Allgemeines / Definition',
 'amyloidose-leichtketten-al-amyloidose': 'Amyloidose (Leichtketten (AL) - Amyloidose)',
 'aplastic-anemia-diagnostics-and-therapy-of-acquired-aplastic-anemia': 'Aplastic Anemia - Diagnostics and Therapy of Acquired Aplastic Anemia',
 'aplastische-anaemie-diagnostik-und-therapie-der-erworbenen-aplastischen-anaemie': 'Aplastische An\xc3\xa4mie - Diagnostik und Therapie der erworbenen Aplastischen An\xc3\xa4mie',
 'aplastische-anaemie-medikamentoese-therapie': 'Aplastische An\xc3\xa4mie - Medikament\xc3\xb6se Therapie',
 'aplastische-anaemie-zulassungsstatus-von-medikamenten': 'Aplastische An\xc3\xa4mie - Zulassungsstatus von Medikamenten',
 'atemvorgang-unwirksamer-atemnot-dyspnoe': 'Atemvorgang, unwirksamer (Atemnot, Dyspnoe)',
 'bauchspeicheldruesenkrebs': 'Bauchspeicheldr\xc3\xbcsenkrebs',
 'beta-thalassaemie': 'Beta Thalass\xc3\xa4mie',
 'breast-cancer-in-women': 'Breast Cancer in Women',
 'brustkrebs-der-frau': 'Brustkrebs der Frau',
 'brustkrebs-des-mannes': 'Brustkrebs des Mannes',
 'central-venous-catheter-related-infections-cri-in-hematology-and-oncology': 'Central Venous Catheter-related Infections (CRI) in Hematology and Oncology',
 'chronic-lymphocytic-leukemia': 'Chronic Lymphocytic Leukemia',
 'chronische-lymphatische-leukaemie-cll': 'Chronische Lymphatische Leuk\xc3\xa4mie (CLL)',
 'chronische-lymphatische-leukaemie-medikamentoese-tumortherapie': 'Chronische Lymphatische Leuk\xc3\xa4mie Medikament\xc3\xb6se Tumortherapie',
 'chronische-lymphatische-leukaemie-studienergebnisse-randomisierte-phase-ii-studien-phase-iii-studien-metaanalysen': 'Chronische Lymphatische Leuk\xc3\xa4mie Studienergebnisse (randomisierte Phase II Studien, Phase III Studien, Metaanalysen)',
 'chronische-lymphatische-leukaemie-zulassungsstatus-von-medikamenten': 'Chronische Lymphatische Leuk\xc3\xa4mie Zulassungsstatus von Medikamenten',
 'chronische-myeloische-leukaemie-cml': 'Chronische Myeloische Leuk\xc3\xa4mie (CML)',
 'chronische-myeloische-leukaemie-medikamentoese-therapie': 'Chronische Myeloische Leuk\xc3\xa4mie - medikament\xc3\xb6se Therapie',
 'chronische-myeloische-leukaemie-studienergebnisse-randomisierte-phase-ii-studien-phase-iii-studien-metaanalysen': 'Chronische Myeloische Leuk\xc3\xa4mie - Studienergebnisse (randomisierte Phase II Studien, Phase III Studien, Metaanalysen)',
 'chronische-myeloische-leukaemie-zulassungsstatus-von-medikamenten': 'Chronische Myeloische Leuk\xc3\xa4mie - Zulassungsstatus von Medikamenten',
 'chronische-myeloproliferative-erkrankungen-cmpe': 'Chronische Myeloproliferative Erkrankungen (CMPE) ',
 'de-at-kolorektales-karzinom-zulassungsstatus-von-medikamenten-deutschland-oesterreich': '(DE/AT) Kolorektales Karzinom - Zulassungsstatus von Medikamenten (Deutschland, \xc3\x96sterreich)',
 'de-at-lungenkarzinom-zulassungsstatus-von-medikamenten': '(DE/AT) Lungenkarzinom - Zulassungsstatus von Medikamenten',
 'diffuses-grosszelliges-b-zell-lymphom': 'Diffuses gro\xc3\x9fzelliges B-Zell-Lymphom',
 'diffuses-grosszelliges-b-zell-lymphom-medikamentoese-tumortherapie-protokolle': 'Diffuses gro\xc3\x9fzelliges B-Zell Lymphom - Medikament\xc3\xb6se Tumortherapie - Protokolle',
 'durchfall-diarrhoe': 'Durchfall (Diarrhoe)',
 'eisenmangel': 'Eisenmangel',
 'eisenmangel-und-eisenmangelanaemie': 'Eisenmangel und Eisenmangelan\xc3\xa4mie',
 'eosinophilie-assoziierte-myeloproliferative-erkrankungen-mpn-eo': 'Eosinophilie - assoziierte Myeloproliferative Erkrankungen (MPN-Eo)',
 'erbrechen-dysfunktionale-gastrointestinale-motilitaet': 'Erbrechen/ Dysfunktionale gastrointestinale Motilit\xc3\xa4t',
 'ernaehrung-mangelernaehrung': 'Ern\xc3\xa4hrung (Mangelern\xc3\xa4hrung)',
 'erschoepfung-fatigue': 'Ersch\xc3\xb6pfung (Fatigue)',
 'essentielle-oder-primaere-thrombozythaemie-et': 'Essentielle (oder prim\xc3\xa4re) Thrombozyth\xc3\xa4mie (ET) ',
 'ewing-sarkom': 'Ewing Sarkom',
 'extranodales-marginalzonen-lymphom-mzol': 'Extranodales Marginalzonen-Lymphom (MZoL)',
 'extranodales-marginalzonen-lymphom-mzol-medikamentoese-tumortherapie-protokolle': 'Extranodales Marginalzonen-Lymphom (MZoL) - Medikament\xc3\xb6se Tumortherapie - Protokolle',
 'extranodales-marginalzonen-lymphom-mzol-zulassung': 'Extranodales Marginalzonen-Lymphom (MZoL) - Zulassung',
 'febrile-neutropenie-mit-lungeninfiltraten-nach-intensiver-chemotherapie-fieber-in-neutropenie': 'Febrile Neutropenie mit Lungeninfiltraten nach intensiver Chemotherapie (Fieber in Neutropenie)',
 'follicular-lymphoma': 'Follicular Lymphoma',
 'follikulaeres-lymphom': 'Follikul\xc3\xa4res Lymphom',
 'follikulaeres-lymphom-medikamentoese-tumortherapie-protokolle': 'Follikul\xc3\xa4res Lymphom - Medikament\xc3\xb6se Tumortherapie - Protokolle',
 'follikulaeres-lymphom-zulassungsstatus-von-medikamenten': 'Follikul\xc3\xa4res Lymphom - Zulassungsstatus von Medikamenten',
 'gastrointestinale-stromatumore-gist': 'Gastrointestinale Stromatumore (GIST)',
 'haarzell-leukaemie': 'Haarzell-Leuk\xc3\xa4mie',
 'haarzell-leukaemie-2013-medikamentoese-tumortherapie': 'Haarzell-Leuk\xc3\xa4mie \xe2\x80\x93 medikament\xc3\xb6se Tumortherapie',
 'haarzell-leukaemie-hzl': 'Haarzell-Leuk\xc3\xa4mie (HZL) ',
 'haarzell-leukaemie-studienergebnisse': 'Haarzell-Leuk\xc3\xa4mie - Studienergebnisse ',
 'haarzell-leukaemie-systemtherapie-protokolle': 'Haarzell-Leuk\xc3\xa4mie - Systemtherapie-Protokolle ',
 'haarzell-leukaemie-zulassungsstatus-von-medikamenten': 'Haarzell-Leuk\xc3\xa4mie - Zulassungsstatus von Medikamenten',
 'haematopoetische-wachstumsfaktoren': 'H\xc3\xa4matopoetische Wachstumsfaktoren',
 'haemophagozytische-lymphohistiozytose-hlh': 'H\xc3\xa4mophagozytische Lymphohistiozytose (HLH)',
 'hairy-cell-leukemia': 'Hairy-Cell Leukemia',
 'hautschaedigung': 'Hautsch\xc3\xa4digung',
 'heranwachsende-und-junge-erwachsene-aya': 'Heranwachsende und junge Erwachsene (AYA)',
 'heranwachsende-und-junge-erwachsene-aya-adolescents-and-young-adults': 'Heranwachsende und junge Erwachsene (AYA, Adolescents and Young Adults)',
 'hereditary-spherocytosis-spherocytic-anemia': 'Hereditary Spherocytosis (Spherocytic Anemia)',
 'hodgkin-lymphom': 'Hodgkin-Lymphom',
 'hodgkin-lymphom-medikamentoese-tumortherapie': 'Hodgkin Lymphom - Medikament\xc3\xb6se Tumortherapie',
 'hodgkin-lymphom-zulassungsstatus-von-medikamenten': 'Hodgkin Lymphom - Zulassungsstatus von Medikamenten',
 'hodgkin-lymphome': 'Hodgkin-Lymphome ',
 'hodgkin2019s-lymphoma': 'Hodgkin\xe2\x80\x99s Lymphoma',
 'immunthrombozytopenie-2013-medikamentoese-therapie': 'Immunthrombozytopenie \xe2\x80\x93 medikament\xc3\xb6se Therapie',
 'immunthrombozytopenie-itp': 'Immunthrombozytopenie (ITP)',
 'immunthrombozytopenie-schweiz-zulassungsstatus-von-medikamenten': 'Immunthrombozytopenie - Schweiz - Zulassungsstatus von Medikamenten',
 'immunthrombozytopenie-zulassungsstatus-von-medikamenten-deutschland-oesterreich': 'Immunthrombozytopenie - Zulassungsstatus von Medikamenten - Deutschland/\xc3\x96sterreich',
 'indolente-non-hodgkin-lymphome-nhl': 'Indolente Non Hodgkin-Lymphome (NHL)',
 'infektioese-komplikationen-nach-hochdosistherapie-und-autologer-stammzelltransplantation': 'Infekti\xc3\xb6se Komplikationen nach Hochdosistherapie und autologer Stammzelltransplantation ',
 'infektionen-nach-hochdosistherapie': 'Infektionen nach Hochdosistherapie',
 'infektionsgefahr-infektion': 'Infektionsgefahr/ Infektion',
 'invasive-pilzinfektionen-primaerprophylaxe': 'Invasive Pilzinfektionen-Prim\xc3\xa4rprophylaxe ',
 'invasive-pilzinfektionen-therapie': 'Invasive Pilzinfektionen-Therapie ',
 'keimreduzierte-kost': 'Keimreduzierte Kost',
 'klinefelter-syndrom-und-krebs': 'Klinefelter-Syndrom und Krebs',
 'klinefelter-syndrome-and-cancer': 'Klinefelter Syndrome and Cancer',
 'knochentumore': 'Knochentumore',
 'koerperbildstoerung': 'K\xc3\xb6rperbildst\xc3\xb6rung',
 'kolon-und-rektumkarzinom-2013-medikamentoese-tumortherapie': 'Kolon- und Rektumkarzinom \xe2\x80\x93 medikament\xc3\xb6se Tumortherapie',
 'kolon-und-rektumkarzinom-studienergebnisse-randomisierte-phase-ii-studien-phase-iii-studien-metaanalysen': 'Kolon- und Rektumkarzinom - Studienergebnisse (randomisierte Phase II Studien, Phase III Studien, Metaanalysen)',
 'kolonkarzinom': 'Kolonkarzinom',
 'komplementaere-therapie': 'Komplement\xc3\xa4re Therapie ',
 'kugelzellen-anaemie': 'Kugelzellen-An\xc3\xa4mie',
 'leichtketten-al-amyloidose-medikamentoese-therapie': 'Leichtketten (AL) - Amyloidose - Medikament\xc3\xb6se Therapie',
 'leichtketten-al-amyloidose-zulassungsstatus-von-medikamenten-deutschland': 'Leichtketten (AL) - Amyloidose - Zulassungsstatus von Medikamenten - Deutschland',
 'lung-infiltrates-in-patients-with-febrile-neutropenia': 'Lung Infiltrates in Patients with Febrile Neutropenia',
 'lungenkarzinom-kleinzellig-sclc': 'Lungenkarzinom, kleinzellig (SCLC)',
 'lungenkarzinom-nicht-kleinzellig-nsclc': 'Lungenkarzinom, nicht-kleinzellig (NSCLC)',
 'lungenkarzinom-nicht-kleinzellig-nsclc-2013-medikamentoese-tumortherapie': 'Lungenkarzinom, nicht-kleinzellig (NSCLC)  \xe2\x80\x93 medikament\xc3\xb6se Tumortherapie',
 'lungenkarzinom-studienergebnisse-randomisierte-phase-ii-studien-phase-iii-studien-metaanalysen': 'Lungenkarzinom - Studienergebnisse (randomisierte Phase II Studien, Phase III Studien, Metaanalysen)',
 'maligne-knochentumore-des-erwachsenen': 'Maligne Knochentumore des Erwachsenen',
 'mammakarzinom-der-frau': 'Mammakarzinom der Frau ',
 'mammakarzinom-der-frau-studienergebnisse-phase-iii-studien-metaanalysen': 'Mammakarzinom der Frau Studienergebnisse (Phase III Studien, Metaanalysen)',
 'mammakarzinom-des-mannes': 'Mammakarzinom des Mannes ',
 'mammakarzinom-medikamentoese-tumortherapie': 'Mammakarzinom - medikament\xc3\xb6se Tumortherapie',
 'mammakarzinom-zulassungsstatus-von-medikamenten': 'Mammakarzinom - Zulassungsstatus von Medikamenten',
 'management-der-sepsis-bei-neutropenen-patienten': 'Management der Sepsis bei neutropenen Patienten ',
 'management-of-sepsis-in-neutropenic-patients': 'Management of Sepsis in Neutropenic Patients',
 'mantelzell-lymphom': 'Mantelzell-Lymphom',
 'mantelzell-lymphom-medikamentoese-tumortherapie-protokolle': 'Mantelzell-Lymphom - Medikament\xc3\xb6se Tumortherapie - Protokolle',
 'mantelzell-lymphom-zulassungsstatus-der-medikamente': 'Mantelzell-Lymphom - Zulassungsstatus der Medikamente',
 'mantle-cell-lymphoma': 'Mantle Cell Lymphoma',
 'medikamentoese-tumortherapie-anordnung-durchfuehrung-und-nachsorge': 'Medikament\xc3\xb6se Tumortherapie: Anordnung, Durchf\xc3\xbchrung und Nachsorge',
 'medikamentoese-tumortherapie-schema-2013-beispiel': 'Medikament\xc3\xb6se Tumortherapie Schema \xe2\x80\x93 Beispiel',
 'melanom': 'Melanom',
 'melanom-studienergebnisse-randomisierte-phase-ii-studien-phase-iii-studien-metaanalysen': 'Melanom - Studienergebnisse (randomisierte Phase II Studien, Phase III Studien, Metaanalysen)',
 'mobilitaet-beeintraechtigte-koerperliche': 'Mobilit\xc3\xa4t, beeintr\xc3\xa4chtigte (k\xc3\xb6rperliche)',
 'monoclonal-b-cell-lymphocytosis': 'Monoclonal B-Cell Lymphocytosis',
 'monoklonale-b-lymphozytose': 'Monoklonale B Lymphozytose',
 'monoklonale-gammopathie-unklarer-signifikanz-mgus': 'Monoklonale Gammopathie Unklarer Signifikanz (MGUS)',
 'morbus-waldenstroem': 'Morbus Waldenstr\xc3\xb6m',
 'multiples-myelom': 'Multiples Myelom',
 'multiples-myelom-deutschland-oesterreich-zulassungsstatus-von-medikamenten': 'Multiples Myelom - Deutschland / \xc3\x96sterreich - Zulassungsstatus von Medikamenten',
 'multiples-myelom-studienergebnisse-randomisierte-phase-ii-studien-phase-iii-studien-metaanalysen': 'Multiples Myelom - Studienergebnisse (randomisierte Phase II Studien,Phase III Studien, Metaanalysen)',
 'multiples-myelom-systemtherapie': 'Multiples Myelom - Systemtherapie',
 'multiples-myelom-zulassungsstatus-von-medikamenten-schweiz': 'Multiples Myelom - Zulassungsstatus von Medikamenten - Schweiz',
 'myelodysplastic-syndromes': 'Myelodysplastic Syndromes',
 'myelodysplastische-syndrome-mds': 'Myelodysplastische Syndrome (MDS)',
 'myelodysplastisches-syndrom-2013-medikamentoese-therapie': 'Myelodysplastisches Syndrom \xe2\x80\x93 medikament\xc3\xb6se Therapie',
 'myelodysplastisches-syndrom-mds': 'Myelodysplastisches Syndrom (MDS)',
 'myelodysplastisches-syndrom-medikamentoese-therapie': 'Myelodysplastisches Syndrom - medikament\xc3\xb6se Therapie',
 'nierenkrebs': 'Nierenkrebs',
 'nierenzellkarzinom-hypernephrom': 'Nierenzellkarzinom (Hypernephrom)',
 'nierenzellkarzinom-medikamentoese-tumortherapie': 'Nierenzellkarzinom - Medikament\xc3\xb6se Tumortherapie',
 'nierenzellkarzinom-studienergebnisse-randomisierte-phase-ii-studien-phase-iii-studien-metaanalysen': 'Nierenzellkarzinom - Studienergebnisse (randomisierte Phase II Studien, Phase III Studien, Metaanalysen)',
 'nierenzellkarzinom-zulassungsstatus-von-medikamenten-in-deutschland': 'Nierenzellkarzinom - Zulassungsstatus von Medikamenten in Deutschland',
 'nodales-marginalzonen-lymphom': 'Nodales Marginalzonen-Lymphom ',
 'obstipation-verstopfung': 'Obstipation (Verstopfung)',
 'pankreaskarzinom': 'Pankreaskarzinom',
 'pankreaskarzinom-studienergebnisse': 'Pankreaskarzinom - Studienergebnisse ',
 'pankreaskarzinom-therapieprotokolle': 'Pankreaskarzinom - Therapieprotokolle',
 'paroxysmal-nocturnal-hemoglobinuria-pnh': 'Paroxysmal Nocturnal Hemoglobinuria (PNH)',
 'paroxysmale-naechtliche-haemoglobinurie-pnh': 'Paroxysmale n\xc3\xa4chtliche H\xc3\xa4moglobinurie (PNH)',
 'partiell-implantierte-zentralvenoese-katheter': 'Partiell implantierte zentralven\xc3\xb6se Katheter',
 'periphere-venenverweilkanuelen': 'Periphere Venenverweilkan\xc3\xbclen',
 'pflege-von-haematologisch-onkologischen-patienten-mit-uebelkeit-und-oder-erbrechen': 'Pflege von h\xc3\xa4matologisch-onkologischen Patienten mit \xc3\x9cbelkeit und/ oder Erbrechen',
 'pilzinfektionen': 'Pilzinfektionen',
 'polycythaemia-vera-pv': 'Polycythaemia Vera (PV) ',
 'portkatheter': 'Portkatheter',
 'praevention-von-infektionen-und-thrombosen-nach-splenektomie-oder-funktioneller-asplenie': 'Pr\xc3\xa4vention von Infektionen und Thrombosen nach Splenektomie oder funktioneller Asplenie ',
 'primaere-myelofibrose-pmf': 'Prim\xc3\xa4re Myelofibrose (PMF) ',
 'prophylaxis-of-invasive-fungal-infections-in-patients-with-hematologic-malignancies': 'Prophylaxis of Invasive Fungal Infections in Patients with Hematologic Malignancies',
 'prostatakarzinom': 'Prostatakarzinom',
 'prostatakarzinom-studienergebnisse-randomisierte-phase-ii-studien-phase-iii-studien-metaanalysen': 'Prostatakarzinom Studienergebnisse (randomisierte Phase II Studien, Phase III Studien, Metaanalysen)',
 'prostatakarzinom-zulassungsstatus-von-medikamenten-endokrine-therapie': 'Prostatakarzinom - Zulassungsstatus von Medikamenten - Endokrine Therapie',
 'prostatakrebs-prostatakarzinom': 'Prostatakrebs (Prostatakarzinom)',
 'prostate-cancer': 'Prostate Cancer ',
 'rektumkarzinom': 'Rektumkarzinom',
 'renal-cell-carcinoma-hypernephroma': 'Renal Cell Carcinoma (Hypernephroma)',
 'respiratory-syncytial-virus-rsv-2013-infektionen-bei-patienten-nach-haematopoetischer-stammzelltransplantation': 'Respiratory Syncytial Virus (RSV) \xe2\x80\x93 Infektionen bei Patienten nach h\xc3\xa4matopoetischer Stammzelltransplantation',
 'sarkome': 'Sarkome',
 'schlafstoerung-insomnia': 'Schlafst\xc3\xb6rung (Insomnia)',
 'schmerz': 'Schmerz',
 'schweiz-kolorektales-karzinom-zulassungsstatus-von-medikamenten': '(Schweiz) Kolorektales Karzinom - Zulassungsstatus von Medikamenten',
 'schweiz-lungenkarzinom-zulassungsstatus-von-medikamenten': '(Schweiz) Lungenkarzinom - Zulassungsstatus von Medikamenten ',
 'sepsis': 'Sepsis',
 'sichelzellkrankheiten': 'Sichelzellkrankheiten',
 'sphaerozytose-hereditaer-kugelzellenanaemie': 'Sph\xc3\xa4rozytose, heredit\xc3\xa4r (Kugelzellenan\xc3\xa4mie) ',
 'systemtherapie': 'Systemtherapie ',
 'systemtherapie-protokolle': 'Systemtherapie - Protokolle ',
 'test-ajung': 'test ajung',
 'test-ajung4': 'test ajung4',
 'test2': 'test2',
 'thrombosen-und-embolien-bei-tumorpatienten': 'Thrombosen und Embolien bei Tumorpatienten',
 'thrombozytentransfusion': 'Thrombozytentransfusion',
 'thrombozytopenien': 'Thrombozytopenien ',
 'uebelkeit-nausea': '\xc3\x9cbelkeit (Nausea)',
 'venoese-thrombembolien-bei-tumorpatienten-studienergebnisse': 'Ven\xc3\xb6se Thrombembolien bei Tumorpatienten - Studienergebnisse ',
 'venoese-thrombembolien-vte-bei-tumorpatienten': 'Ven\xc3\xb6se Thrombembolien (VTE) bei Tumorpatienten',
 'vte-test': 'vte test',
 'weichteilsarkome': 'Weichteilsarkome',
 'weichteilsarkome-2013-studienergebnisse': 'Weichteilsarkome \xe2\x80\x93 Studienergebnisse',
 'weichteilsarkome-medikamentoese-tumortherapie': 'Weichteilsarkome - medikament\xc3\xb6se Tumortherapie',
 'zentrale-venenkatheter': 'Zentrale Venenkatheter',
 'zentrale-venenkatheter-zvk': 'Zentrale Venenkatheter (ZVK)',
 'zvk-infektionen': 'ZVK Infektionen'}
language_vocab = SimpleVocabulary([
    SimpleTerm(value=u'de', title=_(u'German')),
    SimpleTerm(value=u'en', title=_(u'English')),
])

area_vocab = SimpleVocabulary([
    SimpleTerm(value=u'onkopedia', title=_(u'Onkopedia')),
    SimpleTerm(value=u'onkopedia-p', title=_(u'Onkopedia-P')),
    SimpleTerm(value=u'my-onkopedia', title=_(u'My Onkopedia')),
    SimpleTerm(value=u'knowledge-database', title=_(u'Knowledge database')),
])

state_vocab = SimpleVocabulary([
    SimpleTerm(value=u'draft', title=_(u'Draft')),
    SimpleTerm(value=u'current', title=_(u'Current')),
    SimpleTerm(value=u'archived', title=_(u'Archived')),
])

classification_vocab = SimpleVocabulary([
    SimpleTerm(value=u'guideline', title=_(u'Guideline')),
    SimpleTerm(value=u'studies', title=_(u'Studies')),
    SimpleTerm(value=u'certifications', title=_(u'Certifications')),
])


id_terms = list()
for id in sorted(id2titles):
    title = unicode(id2titles[id], 'utf8')
    id_terms.append(SimpleTerm(id, id, title))
id_vocab = SimpleVocabulary(id_terms)



class IGuideline(model.Schema):
    """ Interface for Guideline behavior """
    
    model.fieldset(
        'fieldset_guideline',
        label=_(u'Guideline'),
        fields=['gl_language', 'gl_state', 'gl_area', 'gl_id', 'gl_archive_id', 'gl_classification']
    )
    gl_language = schema.Choice(
        title=_(u'Guideline language'),
        description=_(u"Language of guideline"),
        required=True,
        default=u'de',
        vocabulary=language_vocab
    )

    gl_state = schema.Choice(
        title=_(u'Guideline workflow state'),
        description=_(u"State of guideline"),
        required=True,
        default=u'draft',
        vocabulary=state_vocab
    )
#    
    gl_area = schema.Choice(
        title=_(u'Guideline area'),
        description=_(u"Content area for guideline"),
        required=True,
        default=u'onkopedia',
        vocabulary=area_vocab
    )

    gl_classification = schema.Choice(
        title=_(u'Guideline classification'),
        description=_(u'Classification of guideline'),
        required=True,
        default=u'guideline',
        vocabulary=classification_vocab
    )
#
    gl_id = schema.Choice(
        title=_(u'Internal id'),
        description=_(u'Internal id representing the clinical picture'),
        required=True,
        default=None,
        vocabulary=id_vocab
    )

    gl_archive_id = schema.TextLine(
        title=_(u'ID in archive'),
        description=_(u'ID in archive'),
        required=False,
        default=u'',
    )

alsoProvides(IGuideline, IFormFieldProvider)


class Guideline(object):
    """ Adapter for Guideline """

    implements(IGuideline)
    adapts(IDexterityContent)

    def __init__(self,context):
        self.context = context

    gl_language = context_property('gl_language')
    gl_state = context_property('gl_state')
    gl_area = context_property('gl_area')
    gl_id = context_property('gl_id')
    gl_archive_id = context_property('gl_archive_id')
    gl_classification = context_property('gl_classification')

