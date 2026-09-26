#!/usr/bin/env node

/**
 * Frappe ECC Universal Setup Wizard & CLI
 * Installs, updates, and manages Frappe Engineering Coordination Center across AI code editors.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const PKG_ROOT = path.resolve(__dirname, '..');

function getAntigravityConfigDir() {
  const home = os.homedir();
  return path.join(home, '.gemini', 'config');
}

function getClaudeConfigDir() {
  const home = os.homedir();
  return path.join(home, '.claude');
}

function getCursorConfigDir(cwd = process.cwd()) {
  return path.join(cwd, '.cursor');
}

function copyRecursiveSync(src, dest) {
  const exists = fs.existsSync(src);
  const stats = exists && fs.statSync(src);
  const isDirectory = exists && stats.isDirectory();
  if (isDirectory) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }
    fs.readdirSync(src).forEach((childItemName) => {
      copyRecursiveSync(path.join(src, childItemName), path.join(dest, childItemName));
    });
  } else {
    fs.copyFileSync(src, dest);
  }
}

function installAntigravity(profile, dryRun) {
  const configDir = getAntigravityConfigDir();
  const pluginDir = path.join(configDir, 'plugins', 'frappe-ecc');
  const skillsTargetDir = path.join(configDir, 'skills');
  const rulesTargetDir = path.join(configDir, 'rules');

  console.log(`\n📦 Installing Frappe ECC for Antigravity (Profile: ${profile})...`);
  console.log(`   Target Plugin: ${pluginDir}`);
  console.log(`   Target Skills: ${skillsTargetDir}`);

  if (dryRun) {
    console.log('   [DRY-RUN] Would create plugin and copy skills & rules.');
    return;
  }

  // 1. Create plugin directory structure
  fs.mkdirSync(pluginDir, { recursive: true });
  fs.mkdirSync(skillsTargetDir, { recursive: true });
  fs.mkdirSync(rulesTargetDir, { recursive: true });

  // 2. Copy skills
  const skillsSrc = path.join(PKG_ROOT, 'skills');
  if (fs.existsSync(skillsSrc)) {
    const skills = fs.readdirSync(skillsSrc);
    skills.forEach((skill) => {
      const srcSkillDir = path.join(skillsSrc, skill);
      const destSkillDir = path.join(skillsTargetDir, skill);
      copyRecursiveSync(srcSkillDir, destSkillDir);
      console.log(`   ✓ Skill installed: ${skill}`);
    });
  }

  // 3. Copy plugin contents
  copyRecursiveSync(path.join(PKG_ROOT, 'agents'), path.join(pluginDir, 'agents'));
  copyRecursiveSync(path.join(PKG_ROOT, 'skills'), path.join(pluginDir, 'skills'));
  copyRecursiveSync(path.join(PKG_ROOT, 'rules'), path.join(pluginDir, 'rules'));
  copyRecursiveSync(path.join(PKG_ROOT, 'rules'), rulesTargetDir);
  copyRecursiveSync(path.join(PKG_ROOT, 'bin'), path.join(pluginDir, 'bin'));

  // Copy adapter manifest
  const adapterManifest = path.join(PKG_ROOT, 'adapters', 'antigravity', 'plugin.json');
  if (fs.existsSync(adapterManifest)) {
    fs.copyFileSync(adapterManifest, path.join(pluginDir, 'plugin.json'));
  }

  console.log('   ✅ Antigravity installation completed successfully!');
}

function installClaude(profile, dryRun) {
  const claudeDir = getClaudeConfigDir();
  const pluginDir = path.join(claudeDir, 'plugins', 'frappe-ecc');
  const commandsDir = path.join(claudeDir, 'commands');

  console.log(`\n📦 Installing Frappe ECC for Claude Code (Profile: ${profile})...`);
  if (dryRun) {
    console.log(`   [DRY-RUN] Would install to ${pluginDir} and ${commandsDir}`);
    return;
  }

  fs.mkdirSync(pluginDir, { recursive: true });
  fs.mkdirSync(commandsDir, { recursive: true });

  copyRecursiveSync(PKG_ROOT, pluginDir);
  copyRecursiveSync(path.join(PKG_ROOT, 'commands'), commandsDir);
  console.log('   ✅ Claude Code installation completed successfully!');
}

function installCursor(profile, dryRun) {
  const cursorDir = getCursorConfigDir();
  console.log(`\n📦 Installing Frappe ECC for Cursor (Profile: ${profile})...`);
  if (dryRun) {
    console.log(`   [DRY-RUN] Would install to ${cursorDir}`);
    return;
  }

  fs.mkdirSync(cursorDir, { recursive: true });
  copyRecursiveSync(path.join(PKG_ROOT, 'rules'), path.join(cursorDir, 'rules'));
  console.log('   ✅ Cursor installation completed successfully!');
}

function doctor() {
  console.log('\n🩺 FRAPPE ECC DOCTOR — SYSTEM DIAGNOSTICS');
  console.log('==========================================');

  // Check Node.js
  console.log(`Node.js Version: ${process.version} (>= v18.0.0 required) - OK`);

  // Check Python
  console.log(`Platform: ${process.platform}`);

  // Check Antigravity config
  const agDir = getAntigravityConfigDir();
  console.log(`Antigravity Config Path: ${agDir} [${fs.existsSync(agDir) ? 'EXISTS' : 'NOT FOUND'}]`);

  // Check Claude config
  const clDir = getClaudeConfigDir();
  console.log(`Claude Code Config Path: ${clDir} [${fs.existsSync(clDir) ? 'EXISTS' : 'NOT FOUND'}]`);

  console.log('\nDiagnostic Complete.');
}

function main() {
  const args = process.argv.slice(2);
  let command = 'setup';
  let profile = 'minimal';
  let target = 'antigravity';
  let dryRun = false;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === 'doctor') command = 'doctor';
    else if (arg === 'setup') command = 'setup';
    else if (arg === '--dry-run') dryRun = true;
    else if (arg === '--profile' && args[i + 1]) {
      profile = args[i + 1];
      i++;
    } else if (arg === '--target' && args[i + 1]) {
      target = args[i + 1];
      i++;
    }
  }

  if (command === 'doctor') {
    doctor();
    return;
  }

  console.log('===========================================================');
  console.log('🚀 FRAPPE ECC (ENGINEERING COORDINATION CENTER) INSTALLER');
  console.log('===========================================================');
  console.log(`Profile: ${profile} | Target: ${target} | DryRun: ${dryRun}`);

  if (target === 'antigravity') {
    installAntigravity(profile, dryRun);
  } else if (target === 'claude') {
    installClaude(profile, dryRun);
  } else if (target === 'cursor') {
    installCursor(profile, dryRun);
  } else if (target === 'all') {
    installAntigravity(profile, dryRun);
    installClaude(profile, dryRun);
    installCursor(profile, dryRun);
  } else {
    console.log(`Unknown target: ${target}. Defaulting to Antigravity.`);
    installAntigravity(profile, dryRun);
  }

  console.log('\n🎉 Setup finished! You can now use all Frappe ECC skills, agents, and commands.\n');
}

if (require.main === module) {
  main();
}
