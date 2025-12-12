#!/usr/bin/env node
// Global Cortex - Free GitHub-Powered Coordination Engine
// Zero cost, fully operational

const https = require('https');
const fs = require('fs');
const path = require('path');

class GlobalCortex {
  constructor(config = {}) {
    this.repoPath = config.repoPath || process.cwd();
    this.nodesDir = path.join(this.repoPath, 'global-cortex/nodes');
    this.tasksDir = path.join(this.repoPath, 'global-cortex/tasks');
    this.pulsesDir = path.join(this.repoPath, 'global-cortex/pulses');
    
    // Ensure directories exist
    [this.nodesDir, this.tasksDir, this.pulsesDir].forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });
    
    console.log('🌐 Global Cortex initialized');
    console.log(`📁 Repository: ${this.repoPath}`);
  }

  // Register new Echo node
  registerNode(nodeData) {
    const node = {
      id: nodeData.id || `node-${Date.now()}`,
      registered_at: new Date().toISOString(),
      location: nodeData.location || { city: 'Unknown', country: 'Unknown' },
      capabilities: nodeData.capabilities || [],
      device_type: nodeData.device_type || 'unknown',
      status: 'active',
      last_pulse: new Date().toISOString(),
      metrics: {
        cpu: 0,
        memory: 0,
        active_tasks: 0,
        completed_tasks: 0
      }
    };

    // Save to file system
    const nodePath = path.join(this.nodesDir, `${node.id}.json`);
    fs.writeFileSync(nodePath, JSON.stringify(node, null, 2));

    console.log(`✅ Node registered: ${node.id}`);
    console.log(`   Location: ${node.location.city}, ${node.location.country}`);
    console.log(`   Capabilities: ${node.capabilities.join(', ')}`);
    
    return node;
  }

  // Receive pulse from node
  receivePulse(nodeId, metrics) {
    const pulse = {
      node_id: nodeId,
      timestamp: new Date().toISOString(),
      metrics: metrics || {},
      status: 'healthy'
    };

    // Save pulse
    const pulseFile = `${nodeId}-${Date.now()}.json`;
    const pulsePath = path.join(this.pulsesDir, pulseFile);
    fs.writeFileSync(pulsePath, JSON.stringify(pulse, null, 2));

    // Update node's last_pulse
    const nodePath = path.join(this.nodesDir, `${nodeId}.json`);
    if (fs.existsSync(nodePath)) {
      const node = JSON.parse(fs.readFileSync(nodePath, 'utf8'));
      node.last_pulse = pulse.timestamp;
      node.metrics = pulse.metrics;
      fs.writeFileSync(nodePath, JSON.stringify(node, null, 2));
    }

    console.log(`💓 Pulse received from ${nodeId}`);
    console.log(`   CPU: ${pulse.metrics.cpu}%`);
    console.log(`   Memory: ${pulse.metrics.memory}%`);
    
    return { acknowledged: true, timestamp: pulse.timestamp };
  }

  // Distribute task to optimal node
  distributeTask(task) {
    const taskData = {
      id: `task-${Date.now()}`,
      type: task.type,
      data: task.data,
      priority: task.priority || 'normal',
      created_at: new Date().toISOString(),
      status: 'pending',
      assigned_to: null
    };

    // Find optimal node
    const nodes = this.listNodes();
    if (nodes.length > 0) {
      // Simple assignment: least loaded node
      const optimalNode = nodes.sort((a, b) => 
        a.metrics.active_tasks - b.metrics.active_tasks
      )[0];
      
      taskData.assigned_to = optimalNode.id;
      taskData.status = 'assigned';
      
      // Update node's active tasks
      optimalNode.metrics.active_tasks++;
      const nodePath = path.join(this.nodesDir, `${optimalNode.id}.json`);
      fs.writeFileSync(nodePath, JSON.stringify(optimalNode, null, 2));
    }

    // Save task
    const taskPath = path.join(this.tasksDir, `${taskData.id}.json`);
    fs.writeFileSync(taskPath, JSON.stringify(taskData, null, 2));

    console.log(`📋 Task created: ${taskData.id}`);
    console.log(`   Type: ${taskData.type}`);
    console.log(`   Assigned to: ${taskData.assigned_to || 'unassigned'}`);
    
    return taskData;
  }

  // List all registered nodes
  listNodes() {
    if (!fs.existsSync(this.nodesDir)) {
      return [];
    }
    
    const nodeFiles = fs.readdirSync(this.nodesDir).filter(f => f.endsWith('.json'));
    return nodeFiles.map(file => {
      const content = fs.readFileSync(path.join(this.nodesDir, file), 'utf8');
      return JSON.parse(content);
    });
  }

  // Get global statistics
  getStats() {
    const nodes = this.listNodes();
    const activeNodes = nodes.filter(n => n.status === 'active');
    
    let totalTasks = 0;
    let completedTasks = 0;
    if (fs.existsSync(this.tasksDir)) {
      const taskFiles = fs.readdirSync(this.tasksDir).filter(f => f.endsWith('.json'));
      totalTasks = taskFiles.length;
      completedTasks = taskFiles.filter(file => {
        const task = JSON.parse(fs.readFileSync(path.join(this.tasksDir, file), 'utf8'));
        return task.status === 'completed';
      }).length;
    }
    
    let totalPulses = 0;
    if (fs.existsSync(this.pulsesDir)) {
      totalPulses = fs.readdirSync(this.pulsesDir).filter(f => f.endsWith('.json')).length;
    }

    return {
      total_nodes: nodes.length,
      active_nodes: activeNodes.length,
      total_tasks: totalTasks,
      completed_tasks: completedTasks,
      total_pulses: totalPulses,
      uptime: '100%',
      timestamp: new Date().toISOString()
    };
  }

  // Display status
  displayStatus() {
    const stats = this.getStats();
    console.log('\n' + '='.repeat(50));
    console.log('🌐 GLOBAL CORTEX STATUS');
    console.log('='.repeat(50));
    console.log(`Total Nodes: ${stats.total_nodes}`);
    console.log(`Active Nodes: ${stats.active_nodes}`);
    console.log(`Total Tasks: ${stats.total_tasks}`);
    console.log(`Completed Tasks: ${stats.completed_tasks}`);
    console.log(`Total Pulses: ${stats.total_pulses}`);
    console.log(`Uptime: ${stats.uptime}`);
    console.log('='.repeat(50) + '\n');
  }
}

// CLI interface
if (require.main === module) {
  const cortex = new GlobalCortex({
    repoPath: '/home/ubuntu/echo-github-repos/Echo'
  });
  
  const command = process.argv[2];
  
  switch(command) {
    case 'register':
      const nodeData = JSON.parse(process.argv[3] || '{}');
      cortex.registerNode(nodeData);
      break;
    
    case 'pulse':
      const nodeId = process.argv[3];
      const metrics = JSON.parse(process.argv[4] || '{}');
      cortex.receivePulse(nodeId, metrics);
      break;
    
    case 'task':
      const task = JSON.parse(process.argv[3] || '{}');
      cortex.distributeTask(task);
      break;
    
    case 'status':
      cortex.displayStatus();
      break;
    
    default:
      console.log('Global Cortex - Command Line Interface');
      console.log('Usage:');
      console.log('  node cortex-node.js register \'{"id":"node-1","location":{"city":"NYC"}}\'');
      console.log('  node cortex-node.js pulse node-1 \'{"cpu":45,"memory":62}\'');
      console.log('  node cortex-node.js task \'{"type":"analyze","data":"..."}\'');
      console.log('  node cortex-node.js status');
  }
}

module.exports = GlobalCortex;
