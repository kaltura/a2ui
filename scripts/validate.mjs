// Checks every published catalog folder. Run: node scripts/validate.mjs [root]
//
// v1 and v2: JSON parses and catalogId equals the publish URL.
// v3: the catalog passes the A2UI 1.0 catalog meta-schema, common_types.json is the file
// from @a2ui/web_core, and every example is a valid list of agent-to-renderer messages
// that names this catalog.
import Ajv2020 from 'ajv/dist/2020.js';
import { readdirSync, readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';

const root = resolve(process.argv[2] ?? '.');
const schemas = resolve('node_modules/@a2ui/web_core/src/v1_0/schemas');
const BASE = 'https://kaltura.github.io/a2ui';
const CATALOG_REF_ID = 'https://a2ui.org/specification/v1_0/catalog.json';

const read = path => readFileSync(path, 'utf8');
const json = path => JSON.parse(read(path));
const jsonFiles = dir => readdirSync(dir).filter(name => name.endsWith('.json')).sort().map(name => join(dir, name));
const errors = [];
const fail = message => errors.push(message);
const newAjv = () => new Ajv2020({ strict: false, validateFormats: false, allErrors: true, allowUnionTypes: true });

for (const version of ['v1', 'v2', 'v3']) {
  const catalog = json(join(root, version, 'catalog.json'));
  if (catalog.catalogId !== `${BASE}/${version}/catalog.json`) fail(`${version}: catalogId is ${catalog.catalogId}`);
  for (const file of jsonFiles(join(root, version, 'examples'))) json(file);
}

const catalogPath = join(root, 'v3/catalog.json');
const catalog = json(catalogPath);

if (catalog.$id !== catalog.catalogId) fail('v3: $id and catalogId differ');
if (catalog.protocolVersion !== '1.0') fail(`v3: protocolVersion is ${catalog.protocolVersion}`);
if (read(join(root, 'v3/common_types.json')) !== read(join(schemas, 'common_types.json'))) fail('v3: common_types.json is not the @a2ui/web_core file');

const metaAjv = newAjv();
metaAjv.addSchema(json(join(schemas, 'common_types.json')));
const checkCatalog = metaAjv.compile(json(join(schemas, 'catalog_definition.json')));
if (!checkCatalog(catalog)) fail(`v3: catalog.json fails catalog_definition.json: ${metaAjv.errorsText(checkCatalog.errors)}`);

const messageAjv = newAjv();
messageAjv.addSchema(json(join(schemas, 'common_types.json')));
messageAjv.addSchema(json(join(schemas, 'agent_to_renderer.json')));
messageAjv.addSchema({ ...catalog, $id: CATALOG_REF_ID });
const checkMessages = messageAjv.compile(json(join(schemas, 'agent_to_renderer_list.json')));

const examples = jsonFiles(join(root, 'v3/examples'));
if (examples.length === 0) fail('v3: no examples');
for (const file of examples) {
  const example = json(file);
  const name = file.slice(root.length + 1);
  if (typeof example.name !== 'string' || typeof example.description !== 'string' || !Array.isArray(example.messages)) {
    fail(`${name}: needs name, description and messages`);
    continue;
  }
  if (!checkMessages(example.messages)) fail(`${name}: ${messageAjv.errorsText(checkMessages.errors).slice(0, 500)}`);
  const surfaces = example.messages.filter(message => message.createSurface);
  if (surfaces.length === 0 || surfaces.some(message => message.createSurface.catalogId !== catalog.catalogId)) fail(`${name}: createSurface must name ${catalog.catalogId}`);
}

if (errors.length > 0) {
  console.error(errors.map(message => `ERROR ${message}`).join('\n'));
  process.exit(1);
}
console.log(`OK v1, v2 and v3 are valid. v3: ${Object.keys(catalog.components).length} components, ${examples.length} examples.`);
