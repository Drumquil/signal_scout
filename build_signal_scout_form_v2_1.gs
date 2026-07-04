/**
 * Signal Scout — Beta Intake Form Builder
 * Drumquil Signal | v2.1 | June 2026
 *
 * CHANGES FROM v2.0:
 *   - Section 3 wording now clearly separates commercial stock from female breeding stock.
 *   - "Breeding females" renamed to "Female breeding stock".
 *   - Female breeding stock help text now defines:
 *       heifers = females that have not calved
 *       cows = females that have calved previously
 *       CAF = cows with calves at foot only
 *   - Female breeding stock choices simplified to:
 *       Joined / PTIC / NSM Heifers
 *       Joined / PTIC / NSM Cows
 *       Cows with Calves at Foot (CAF)
 *
 * HOW TO RUN:
 * 1. Go to script.google.com
 * 2. Open the existing buildSignalScoutForm project (or create a new one)
 * 3. Replace all code with this script
 * 4. Click Save, then Run → buildSignalScoutForm
 * 5. A NEW form will be created in your Drive — update the link you share with testers
 * 6. Delete or archive the old form
 * 7. The new response Sheet is automatically linked to the new form
 *
 * NOTE: Running this creates a brand new form. It does not edit the existing one.
 * Check the Execution Log (View → Logs) for the new form URL.
 */

function buildSignalScoutForm() {

  var form = FormApp.create('Signal Scout — Buying Criteria Setup');

  form.setDescription(
    'Your answers set up your personal alert profile. Signal Scout will WhatsApp you ' +
    'when a matching listing appears across online cattle listing platforms.\n\n' +
    'Fill in what matters to you — leave anything blank or select "No preference" for ' +
    'criteria you don\'t want enforced. You\'ll still see available details (age, fat score, ' +
    'temperament etc.) in every alert even if you haven\'t set a filter on them.\n\n' +
    'Setup takes about 5 minutes. Once submitted, Tom will have your profile live within ' +
    '24 hours and will confirm via WhatsApp when you\'re receiving alerts.'
  );

  form.setCollectEmail(true);
  form.setShowLinkToRespondAgain(false);
  form.setConfirmationMessage(
    'Thanks — I\'ll get your profile set up within 24 hours and send you a ' +
    'confirmation on WhatsApp when you\'re live.'
  );
  form.setProgressBar(true);


  // SECTION 1 — YOUR DETAILS

  form.addSectionHeaderItem()
    .setTitle('Your Details')
    .setHelpText('This is used to set up your account. Your WhatsApp number is where alerts will be sent.');

  form.addTextItem()
    .setTitle('Your name')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Your WhatsApp number')
    .setHelpText('Include country code — e.g. +61412345678')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Your property name (optional)')
    .setHelpText('Helps us personalise your alerts.')
    .setRequired(false);


  // SECTION 2 — BUYING REGION

  form.addSectionHeaderItem()
    .setTitle('Buying Region')
    .setHelpText(
      'Select the regions you\'re willing to buy from. Signal Scout filters listings ' +
      'by where the cattle are located — not by sale name.\n\n' +
      'You can select multiple regions.'
    );

  var regionItem = form.addCheckboxItem()
    .setTitle('Which regions are you buying from?')
    .setHelpText('Tick all that apply. Select "Any / no preference" to receive alerts from all regions.')
    .setRequired(true);

  regionItem.setChoices([
    regionItem.createChoice('Northern Rivers NSW'),
    regionItem.createChoice('Northern Tablelands NSW'),
    regionItem.createChoice('New England NSW'),
    regionItem.createChoice('Central & Western NSW'),
    regionItem.createChoice('Southern NSW / ACT'),
    regionItem.createChoice('South East QLD'),
    regionItem.createChoice('Central QLD'),
    regionItem.createChoice('North QLD'),
    regionItem.createChoice('Victoria'),
    regionItem.createChoice('South Australia'),
    regionItem.createChoice('Western Australia'),
    regionItem.createChoice('Tasmania'),
    regionItem.createChoice('Any / no preference'),
  ]);

  form.addTextItem()
    .setTitle('Your nearest town or delivery point')
    .setHelpText(
      'Used to estimate freight costs in your alerts. ' +
      'e.g. Casino, Grafton, Lismore, Inverell'
    )
    .setRequired(false);


  // SECTION 3 — STOCK TYPE

  form.addSectionHeaderItem()
    .setTitle('Stock Type')
    .setHelpText(
      'Tell us what types of cattle you want alerts for.\n\n' +
      'Commercial stock and female breeding stock are treated separately.\n' +
      'Heifers means females that have not calved.\n' +
      'Cows means females that have calved previously.'
    );

  // 3a — Sex preference
  var sexItem = form.addMultipleChoiceItem()
    .setTitle('Sex preference')
    .setHelpText(
      'This question applies to commercial stock only.\n\n' +
      'Select the sex you\'re looking for in commercial mobs. ' +
      '"Either" means you\'ll consider steers, heifers, or mixed mobs. ' +
      'If you only want breeding females, leave this blank.'
    )
    .setRequired(false);

  sexItem.setChoices([
    sexItem.createChoice('Steers'),
    sexItem.createChoice('Heifers'),
    sexItem.createChoice('Either — steers, heifers, or mixed is fine'),
  ]);

  // 3b — Stage of production
  var stageItem = form.addCheckboxItem()
    .setTitle('Stage of production')
    .setHelpText(
      'This question applies to commercial stock only.\n\n' +
      'Select the stages you\'re interested in. You can tick more than one.\n\n' +
      'Weaners / Weaned: recently weaned, no permanent teeth — typically 5–12 months.\n' +
      'Yearlings: older than weaners, usually still no permanent teeth — typically 12–20 months.\n' +
      'Backgrounders, Stores & Feeders: growing cattle beyond the weaner stage.\n' +
      '"Any stage" disables stage filtering. If you only want breeding females, leave this blank.'
    )
    .setRequired(false);

  stageItem.setChoices([
    stageItem.createChoice('Weaners / Weaned'),
    stageItem.createChoice('Yearlings'),
    stageItem.createChoice('Backgrounders, Stores & Feeders'),
    stageItem.createChoice('Any stage — no preference'),
  ]);

  // 3c — Female breeding stock
  // Female breeding stock is intentionally separate from commercial sex/stage.
  // Blank commercial answers + female-breeding selections should be interpreted
  // as a non-commercial-only profile by the transform/runtime.
  var breedingItem = form.addCheckboxItem()
    .setTitle('Female breeding stock')
    .setHelpText(
      'Select the female breeding stock you want alerts for.\n\n' +
      'Heifers = females that have not calved.\n' +
      'Cows = females that have calved previously.\n' +
      'CAF = cows with calves at foot only.\n\n' +
      'Leave this blank if you only want commercial stock.'
    )
    .setRequired(false);

  breedingItem.setChoices([
    breedingItem.createChoice('Joined / PTIC / NSM Heifers'),
    breedingItem.createChoice('Joined / PTIC / NSM Cows'),
    breedingItem.createChoice('Cows with Calves at Foot (CAF)'),
  ]);

  // 3d — Bulls
  var bullItem = form.addCheckboxItem()
    .setTitle('Bulls')
    .setHelpText('Tick if you want alerts for bulls.')
    .setRequired(false);

  bullItem.setChoices([
    bullItem.createChoice('Registered / stud bulls'),
    bullItem.createChoice('Commercial bulls'),
  ]);


  // SECTION 4 — NUMBER OF HEAD

  form.addSectionHeaderItem()
    .setTitle('Number of Head')
    .setHelpText('Set the minimum and maximum number of head you want in a single lot. Leave blank for no limit.');

  form.addTextItem()
    .setTitle('Minimum number of head in a lot')
    .setHelpText('Numbers only — e.g. 20. Lots smaller than this will be ignored.')
    .setRequired(false);

  form.addTextItem()
    .setTitle('Maximum number of head in a lot')
    .setHelpText('Numbers only — e.g. 100. Lots larger than this will be ignored.')
    .setRequired(false);


  // SECTION 5 — BREED

  form.addSectionHeaderItem()
    .setTitle('Breed')
    .setHelpText(
      'Select the breeds you\'ll consider. If breed isn\'t recorded on a listing, ' +
      'it will still come through so you don\'t miss anything.\n\n' +
      'Select "Any / no preference" if breed doesn\'t matter to you.'
    );

  var breedItem = form.addCheckboxItem()
    .setTitle('Which breeds will you consider?')
    .setHelpText(
      'BRITISH & EUROPEAN — Angus, Hereford, Murray Grey, Shorthorn, Simmental, ' +
      'Charolais, Limousin, South Devon, Devon, Speckle Park, Wagyu\n\n' +
      'INDICUS / TROPICAL / COMPOSITES — Brahman, Droughtmaster, Santa Gertrudis, ' +
      'Belmont Red, Charbray, Braford, Brangus, Ultrablack, Beefmaster\n\n' +
      'Select "Any / no preference" to disable breed filtering entirely.'
    )
    .setRequired(false);

  breedItem.setChoices([
    breedItem.createChoice('Angus'),
    breedItem.createChoice('Red Angus'),
    breedItem.createChoice('Poll Hereford'),
    breedItem.createChoice('Hereford'),
    breedItem.createChoice('Murray Grey'),
    breedItem.createChoice('Shorthorn'),
    breedItem.createChoice('Simmental'),
    breedItem.createChoice('Charolais'),
    breedItem.createChoice('Limousin'),
    breedItem.createChoice('South Devon'),
    breedItem.createChoice('Devon'),
    breedItem.createChoice('Speckle Park'),
    breedItem.createChoice('Wagyu'),
    breedItem.createChoice('Blonde d\'Aquitaine'),
    breedItem.createChoice('Gelbvieh'),
    breedItem.createChoice('Salers'),
    breedItem.createChoice('Maine-Anjou'),
    breedItem.createChoice('Marchigiana'),
    breedItem.createChoice('Romagnola'),
    breedItem.createChoice('Piedmontese'),
    breedItem.createChoice('Brahman'),
    breedItem.createChoice('Droughtmaster'),
    breedItem.createChoice('Santa Gertrudis'),
    breedItem.createChoice('Belmont Red'),
    breedItem.createChoice('Charbray'),
    breedItem.createChoice('Braford'),
    breedItem.createChoice('Brangus'),
    breedItem.createChoice('Ultrablack'),
    breedItem.createChoice('Beefmaster'),
    breedItem.createChoice('Brahmousin'),
    breedItem.createChoice('Simbrah'),
    breedItem.createChoice('Chiangus'),
    breedItem.createChoice('Akaushi'),
    breedItem.createChoice('Any / no preference'),
  ]);

  var crossItem = form.addMultipleChoiceItem()
    .setTitle('Do you also want alerts for cross-bred cattle where your selected breed is the primary breed?')
    .setHelpText(
      'e.g. if you selected Angus, this would also include "Angus Cross" listings. ' +
      'Ignored if you selected "Any / no preference" above.'
    )
    .setRequired(false);

  crossItem.setChoices([
    crossItem.createChoice('Yes — include crosses'),
    crossItem.createChoice('No — pure breeds only'),
    crossItem.createChoice('Doesn\'t matter — alert me regardless'),
  ]);


  // SECTION 6 — WEIGHT

  form.addSectionHeaderItem()
    .setTitle('Weight')
    .setHelpText(
      'Average liveweight at delivery. Leave blank for no limit.\n\n' +
      'Weight will always appear in your alerts when available, ' +
      'even if you don\'t set limits here.'
    );

  form.addTextItem()
    .setTitle('Minimum average liveweight (kg)')
    .setHelpText('Numbers only — e.g. 180. Lots lighter than this on average will be ignored.')
    .setRequired(false);

  form.addTextItem()
    .setTitle('Maximum average liveweight (kg)')
    .setHelpText('Numbers only — e.g. 380. Lots heavier than this on average will be ignored.')
    .setRequired(false);

  form.addTextItem()
    .setTitle('Maximum weight spread within the mob (kg)')
    .setHelpText(
      'Controls mob evenness — the difference between the lightest and heaviest animal. ' +
      'e.g. 100 means you\'ll accept lots where the spread is up to 100kg. ' +
      'Leave blank to not enforce.'
    )
    .setRequired(false);


  // SECTION 7 — AGE (OPTIONAL)

  form.addSectionHeaderItem()
    .setTitle('Age (Optional)')
    .setHelpText(
      'Age will always appear in your alerts when available. ' +
      'Only fill in the fields below if you want to filter out listings outside your age range. ' +
      'Leave blank if age doesn\'t matter — you\'ll still see it in every alert.'
    );

  var ageGateItem = form.addMultipleChoiceItem()
    .setTitle('Do you want to filter by age?')
    .setHelpText('Select Yes to activate the age filter fields below.')
    .setRequired(false);

  ageGateItem.setChoices([
    ageGateItem.createChoice('No preference — show me all ages'),
    ageGateItem.createChoice('Yes — I want to set an age range'),
  ]);

  form.addTextItem()
    .setTitle('Minimum age (months)')
    .setHelpText('Numbers only — e.g. 6. Only active if you selected Yes above.')
    .setRequired(false);

  form.addTextItem()
    .setTitle('Maximum age (months)')
    .setHelpText('Numbers only — e.g. 18. Only active if you selected Yes above.')
    .setRequired(false);


  // SECTION 8 — CONDITION (OPTIONAL)

  form.addSectionHeaderItem()
    .setTitle('Condition (Optional)')
    .setHelpText(
      'Fat score uses a 1–5 scale. 1 = very lean, 5 = very fat. Most store cattle trade at 1–3.\n\n' +
      'Fat score will always appear in your alerts when available. ' +
      'Only set limits below if you want to exclude listings outside your preferred range. ' +
      'Leave on "No preference" if condition doesn\'t matter.'
    );

  var fatMinItem = form.addListItem()
    .setTitle('Minimum fat score')
    .setRequired(false);

  fatMinItem.setChoices([
    fatMinItem.createChoice('No preference'),
    fatMinItem.createChoice('1'),
    fatMinItem.createChoice('2'),
    fatMinItem.createChoice('3'),
    fatMinItem.createChoice('4'),
    fatMinItem.createChoice('5'),
  ]);

  var fatMaxItem = form.addListItem()
    .setTitle('Maximum fat score')
    .setRequired(false);

  fatMaxItem.setChoices([
    fatMaxItem.createChoice('No preference'),
    fatMaxItem.createChoice('1'),
    fatMaxItem.createChoice('2'),
    fatMaxItem.createChoice('3'),
    fatMaxItem.createChoice('4'),
    fatMaxItem.createChoice('5'),
  ]);


  // SECTION 9 — ACCREDITATIONS & REQUIREMENTS (OPTIONAL)

  form.addSectionHeaderItem()
    .setTitle('Accreditations & Requirements (Optional)')
    .setHelpText(
      'These are hard filters — if you select Yes, only listings that meet the requirement ' +
      'will come through. Select No if it doesn\'t matter to you.\n\n' +
      'Accreditation details will still appear in every alert when available, ' +
      'regardless of what you select here.'
    );

  var euItem = form.addMultipleChoiceItem()
    .setTitle('Require EU accreditation?')
    .setRequired(false);
  euItem.setChoices([
    euItem.createChoice('No — doesn\'t matter'),
    euItem.createChoice('Yes — EU accredited only'),
  ]);

  var neItem = form.addMultipleChoiceItem()
    .setTitle('Require Greenham Never Ever (NE) accreditation?')
    .setRequired(false);
  neItem.setChoices([
    neItem.createChoice('No — doesn\'t matter'),
    neItem.createChoice('Yes — NE accredited only'),
  ]);

  var whpItem = form.addMultipleChoiceItem()
    .setTitle('Exclude listings with a chemical withholding period (WHP)?')
    .setRequired(false);
  whpItem.setChoices([
    whpItem.createChoice('No — doesn\'t matter'),
    whpItem.createChoice('Yes — exclude WHP listings'),
  ]);

  var hgpItem = form.addMultipleChoiceItem()
    .setTitle('Require HGP-free declaration?')
    .setRequired(false);
  hgpItem.setChoices([
    hgpItem.createChoice('No — doesn\'t matter'),
    hgpItem.createChoice('Yes — HGP-free only'),
  ]);

  var polledItem = form.addMultipleChoiceItem()
    .setTitle('Require polled (no horns)?')
    .setRequired(false);
  polledItem.setChoices([
    polledItem.createChoice('No — doesn\'t matter'),
    polledItem.createChoice('Yes — polled only'),
  ]);

  var quietItem = form.addMultipleChoiceItem()
    .setTitle('Require quiet / docile temperament rating?')
    .setRequired(false);
  quietItem.setChoices([
    quietItem.createChoice('No — doesn\'t matter'),
    quietItem.createChoice('Yes — quiet or docile only'),
  ]);


  // SECTION 10 — ANYTHING ELSE

  form.addSectionHeaderItem()
    .setTitle('Anything else?')
    .setHelpText('Not required — use this to flag anything specific that wasn\'t covered above.');

  form.addParagraphTextItem()
    .setTitle('Is there anything specific you\'re looking for that wasn\'t covered above?')
    .setHelpText(
      'e.g. specific vendors you always or never buy from, tick area requirements, ' +
      'delivery preferences, anything else relevant to your buying criteria.'
    )
    .setRequired(false);


  // DONE — log the URL

  Logger.log('Form created successfully.');
  Logger.log('Edit URL: ' + form.getEditUrl());
  Logger.log('Publish URL: ' + form.getPublishedUrl());
  Logger.log('Form ID: ' + form.getId());

}
